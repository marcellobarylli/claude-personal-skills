#!/usr/bin/env python3
"""Egress proxy for the autonomous sandbox. HOST side: runs inside the Slurm job, outside the container.

The container has no network except loopback (apptainer --net --network none). Its only way out is the Unix socket
this proxy listens on. That is never a TCP port. This policy is the security boundary; the agent's prompt is not:

  * CONNECT to port 443 only, and only to hosts that resolve to public addresses, so no cluster-internal services.
  * TLS is intercepted with a CA that exists only for this sandbox, so the method and path of every request are seen.
  * Reads (GET, HEAD, OPTIONS, no request body) go to any public host. The agent keeps read access.
  * Writes are refused unless POST_ALLOW lists them: Anthropic inference, and the read-only git fetch protocol.
    Websocket upgrades, bodies on reads and plain http:// are refused.
  * Anthropic requests get the real token added here. The container holds only a placeholder.
  * One request per connection (Connection: close), so nothing is smuggled after a checked request.

Residual risk: data can still leave inside the URL of a read, and the agent spends the owner's inference quota.

  egress-proxy.py init-ca <ca-dir>
  egress-proxy.py serve <socket> <ca-dir> <token-file> <log-file>
  egress-proxy.py find-token <token-file> <dir>...   exit 1 if the token occurs in any file (it is never printed)
"""
import ipaddress, json, os, re, socket, ssl, subprocess, sys, threading, time

POST_ALLOW = [  # (host regex, path regex), both full-match
    (r"api\.anthropic\.com", r"/v1/messages(/count_tokens)?(\?[^#]*)?"),
    (r"(github\.com|gitlab\.com|codeberg\.org|bitbucket\.org)", r"/[^?#]+/git-upload-pack"),
]
READ_METHODS = {"GET", "HEAD", "OPTIONS"}
TOKEN_HOST = "api.anthropic.com"
HOP = {"connection", "proxy-connection", "keep-alive", "te", "trailer", "transfer-encoding", "upgrade",
       "proxy-authorization", "expect", "content-length", "host"}
HOST_RE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?$")
MAX_HEAD, MAX_BODY = 64 * 1024, 64 * 1024 * 1024
LOCK = threading.Lock()


class Denied(Exception):
    pass


def log(f, *parts):
    line = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + " " + " ".join(str(p) for p in parts)
    with LOCK:
        f.write(line[:2000].replace("\n", " ") + "\n")
        f.flush()


def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def init_ca(d):
    os.makedirs(d, mode=0o700, exist_ok=True)
    if os.path.exists(f"{d}/ca.crt"):
        print(f"exists: {d}/ca.crt")
        return
    old = os.umask(0o077)
    run("openssl", "genrsa", "-out", f"{d}/ca.key", "2048")
    run("openssl", "genrsa", "-out", f"{d}/leaf.key", "2048")
    os.umask(old)
    run("openssl", "req", "-x509", "-new", "-key", f"{d}/ca.key", "-sha256", "-days", "90",
        "-subj", "/CN=autonomous-sandbox egress CA", "-addext", "basicConstraints=critical,CA:TRUE",
        "-addext", "keyUsage=critical,keyCertSign,cRLSign", "-out", f"{d}/ca.crt")
    print(f"{d}/ca.crt")


def is_ip(host):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


class Certs:
    """One leaf certificate per host, signed by the sandbox CA, cached on disk and in memory."""

    def __init__(self, d):
        self.d, self.cache, self.lock = d, {}, threading.Lock()
        os.makedirs(f"{d}/certs", mode=0o700, exist_ok=True)

    def ctx(self, host):
        with self.lock:
            if host in self.cache:
                return self.cache[host]
            crt = f"{self.d}/certs/{host}.crt"
            if not os.path.exists(crt):
                san = f"IP:{host}" if is_ip(host) else f"DNS:{host}"
                with open(crt + ".ext", "w") as e:
                    e.write(f"subjectAltName={san}\nbasicConstraints=CA:FALSE\n"
                            "keyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\n"
                            "subjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid\n")
                run("openssl", "req", "-new", "-key", f"{self.d}/leaf.key", "-subj", "/CN=sandbox-leaf",
                    "-out", crt + ".csr")
                run("openssl", "x509", "-req", "-in", crt + ".csr", "-CA", f"{self.d}/ca.crt",
                    "-CAkey", f"{self.d}/ca.key", "-set_serial", str(int.from_bytes(os.urandom(8), "big")),
                    "-days", "60", "-sha256", "-extfile", crt + ".ext", "-out", crt + ".tmp")
                os.replace(crt + ".tmp", crt)
                for x in (".csr", ".ext"):
                    os.unlink(crt + x)
            c = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            c.load_cert_chain(crt, f"{self.d}/leaf.key")
            c.set_alpn_protocols(["http/1.1"])
            self.cache[host] = c
            return c


class Reader:
    def __init__(self, s):
        self.s, self.buf = s, b""

    def _more(self):
        d = self.s.recv(65536)
        if not d:
            raise EOFError
        self.buf += d

    def head(self):
        while b"\r\n\r\n" not in self.buf:
            if len(self.buf) > MAX_HEAD:
                raise Denied("header too large")
            self._more()
        head, self.buf = self.buf.split(b"\r\n\r\n", 1)
        lines = head.decode("latin-1").split("\r\n")
        parts = lines[0].split(" ")
        if len(parts) != 3:
            raise Denied("bad request line")
        headers = []
        for l in lines[1:]:
            k, sep, v = l.partition(":")
            if not sep or not k or k != k.strip() or " " in k:
                raise Denied("bad header")
            headers.append((k, v.strip()))
        return parts[0], parts[1], headers

    def line(self):
        while b"\r\n" not in self.buf:
            if len(self.buf) > MAX_HEAD:
                raise Denied("chunk line too long")
            self._more()
        l, self.buf = self.buf.split(b"\r\n", 1)
        return l

    def exact(self, n):
        while len(self.buf) < n:
            self._more()
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def body(self, hl):
        if "chunked" in hl.get("transfer-encoding", "").lower():
            out = b""
            while True:
                size = int(self.line().split(b";")[0].strip(), 16)
                if size == 0:
                    while self.line() != b"":
                        pass
                    return out
                out += self.exact(size)
                self.exact(2)
                if len(out) > MAX_BODY:
                    raise Denied("body too large")
        n = int(hl.get("content-length", "0") or 0)
        if n < 0 or n > MAX_BODY:
            raise Denied("bad content-length")
        return self.exact(n)


def resolve_public(host):
    try:
        addrs = [i[4][0] for i in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)]
    except OSError:
        return None
    if not addrs or not all(ipaddress.ip_address(a.split("%")[0]).is_global for a in addrs):
        return None
    v4 = [a for a in addrs if ":" not in a]
    return (v4 or addrs)[0]  # connect to the vetted address, so a second lookup cannot rebind it


UP_CTX = ssl.create_default_context()


def refuse(s, why):
    msg = f"blocked by the sandbox egress policy: {why}\n".encode()
    try:
        s.sendall(b"HTTP/1.1 403 Forbidden\r\nContent-Type: text/plain\r\nConnection: close\r\n"
                  b"Content-Length: %d\r\n\r\n" % len(msg) + msg)
    except OSError:
        pass


def handle(conn, certs, token, logf):
    s, where = conn, "-"
    try:
        conn.settimeout(120)
        method, target, _ = Reader(conn).head()
        where = f"{method} {target}"
        if method != "CONNECT":
            raise Denied("only CONNECT to https is allowed")
        host, _, port = target.rpartition(":")
        host = host.strip("[]").lower()
        if port != "443" or not (HOST_RE.match(host) or is_ip(host)):
            raise Denied("port or host not allowed")
        ip = resolve_public(host)
        if not ip:
            raise Denied("host does not resolve to a public address")
        conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        s = certs.ctx(host).wrap_socket(conn, server_side=True)
        s.settimeout(300)
        r = Reader(s)
        method, path, headers = r.head()
        if path.lower().startswith("https://"):
            path = "/" + path.split("/", 3)[3] if path.count("/") >= 3 else "/"
        where = f"{method} {host} {path[:300]}"
        if not path.startswith("/"):
            raise Denied("bad request target")
        hl = {k.lower(): v for k, v in headers}
        if "upgrade" in hl:
            raise Denied("protocol upgrade")
        body = b""
        if method in READ_METHODS:
            if int(hl.get("content-length", "0") or 0) > 0 or "transfer-encoding" in hl:
                raise Denied("body on a read request")
        elif method == "POST" and any(re.fullmatch(h, host) and re.fullmatch(p, path) for h, p in POST_ALLOW):
            if hl.get("expect", "").lower() == "100-continue":
                s.sendall(b"HTTP/1.1 100 Continue\r\n\r\n")
            body = r.body(hl)
            if host == TOKEN_HOST:
                try:
                    j = json.loads(body)
                except ValueError:
                    raise Denied("inference body is not JSON")
                if not isinstance(j, dict) or "mcp_servers" in j:
                    raise Denied("remote MCP servers in an inference request")
        else:
            raise Denied("write request")
        out = [f"{method} {path} HTTP/1.1", f"Host: {host}"]
        for k, v in headers:
            kl = k.lower()
            if kl in HOP or (host == TOKEN_HOST and kl in ("authorization", "x-api-key")):
                continue
            out.append(f"{k}: {v}")
        if host == TOKEN_HOST:
            out.append(f"Authorization: Bearer {token}")
        if method not in READ_METHODS:
            out.append(f"Content-Length: {len(body)}")
        out.append("Connection: close")
        up = UP_CTX.wrap_socket(socket.create_connection((ip, 443), timeout=30), server_hostname=host)
        up.settimeout(1800)
        up.sendall(("\r\n".join(out) + "\r\n\r\n").encode("latin-1") + body)
        status, n = "-", 0
        while True:
            d = up.recv(65536)
            if not d:
                break
            if status == "-":
                status = d.split(b"\r\n", 1)[0].decode("latin-1", "replace")[9:12]
            n += len(d)
            s.sendall(d)
        up.close()
        log(logf, "ALLOW", where, status, f"up={len(body)}", f"down={n}")
    except Denied as e:
        log(logf, "DENY", where, "--", e)
        refuse(s, e)
    except (EOFError, OSError, ValueError, ssl.SSLError) as e:
        log(logf, "ERROR", where, "--", type(e).__name__, e)
    finally:
        try:
            s.close()
        except OSError:
            pass


def read_token(path):
    for line in open(path).read().splitlines():
        line = line.strip()
        if line.startswith("CLAUDE_CODE_OAUTH_TOKEN="):
            line = line.split("=", 1)[1]
        line = line.strip("'\"")
        if line and not line.startswith("#"):
            if re.search(r"\s", line):
                sys.exit("token file: token contains whitespace")
            return line
    sys.exit("token file: no token found")


def serve(sock_path, ca_dir, token_file, log_path):
    ca_dir, log_path = os.path.abspath(ca_dir), os.path.abspath(log_path)
    token, certs, logf = read_token(token_file), Certs(ca_dir), open(log_path, "a")
    d, name = os.path.split(os.path.abspath(sock_path))
    os.chdir(d)  # AF_UNIX paths are capped at about 107 bytes, so bind a relative name
    if os.path.exists(name):
        os.unlink(name)
    srv = socket.socket(socket.AF_UNIX)
    old = os.umask(0o177)
    srv.bind(name)
    os.umask(old)
    srv.listen(256)
    log(logf, "START", "pid", os.getpid(), "socket", os.path.abspath(name))
    while True:
        c, _ = srv.accept()
        threading.Thread(target=handle, args=(c, certs, token, logf), daemon=True).start()


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "init-ca":
        init_ca(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "find-token":
        tok = read_token(sys.argv[2]).encode()
        for d in sys.argv[3:]:
            for root, _, files in os.walk(d):
                for f in files:
                    try:
                        with open(os.path.join(root, f), "rb") as fh:
                            if tok in fh.read():
                                print("token found in", os.path.join(root, f))
                                sys.exit(1)
                    except OSError:
                        pass
    elif len(sys.argv) == 6 and sys.argv[1] == "serve":
        serve(*sys.argv[2:])
    else:
        sys.exit(__doc__)
