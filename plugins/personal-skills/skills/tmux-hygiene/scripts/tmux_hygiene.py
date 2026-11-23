#!/usr/bin/env python3
"""Login-node memory hygiene for tmux sessions.

  report [--json]        memory of the user slice, then every tmux session with
                         age, idle state, memory and description material
  kill NAME [NAME...]    re-check each session, then kill the eligible ones
  kill-strays PID [...]  re-check each stray process tree, then SIGTERM the eligible ones
  check                  one warning line if non-cache memory is over the soft
                         limit (for a SessionStart hook); silent otherwise

A session is eligible only if it is older than --min-age-hours (default 48) and
nothing in it is active. A stray is a process tree outside every tmux session and
outside every ssh login (a leftover daemon, for example a Codex broker); it is
eligible when older than --stray-min-age-hours (default 1) and idle. Binds no
network port.
"""
import argparse, glob, json, os, signal, subprocess, sys, time

UID = os.getuid()
SLICE = f"/sys/fs/cgroup/user.slice/user-{UID}.slice"
HZ = os.sysconf("SC_CLK_TCK")
PAGE = os.sysconf("SC_PAGE_SIZE")
GiB = 1024 ** 3
SOFT_LIMIT_GIB = float(os.environ.get("TMUX_HYGIENE_SOFT_GIB", "4"))
SHELLS = {"bash", "sh", "zsh", "fish", "dash", "tmux: server"}
CPU_SAMPLE_S = 3.0
CPU_BUSY_FRACTION = 0.20  # of one core, summed over the session's processes
# Per-user infrastructure that is never a stray (matched on the process name).
INFRA = {"systemd", "(sd-pam)", "dbus-daemon", "pipewire", "pipewire-pulse", "pipewire-media-", "wireplumber",
         "pulseaudio", "ssh-agent", "gpg-agent", "sshd", "tmux", "tmux: server", "tmux: client"}
INFRA_PREFIX = ("gvfs", "gnome-keyring", "at-spi", "xdg-", "dconf")


# ---------- memory ----------

def slice_memory():
    def rd(name):
        try:
            return open(f"{SLICE}/{name}").read().strip()
        except OSError:
            return None
    cur = rd("memory.current")
    if cur is None:
        return None
    stat = dict(l.split() for l in rd("memory.stat").splitlines())
    cache = int(stat.get("active_file", 0)) + int(stat.get("inactive_file", 0))
    high, mx = rd("memory.high"), rd("memory.max")
    return {
        "current": int(cur),
        "cache": cache,
        "noncache": int(cur) - cache,
        "high": None if high in (None, "max") else int(high),
        "max": None if mx in (None, "max") else int(mx),
        "soft": int(SOFT_LIMIT_GIB * GiB),
    }


# ---------- processes ----------

def proc_table():
    procs = {}
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        pid = int(d)
        try:
            if os.stat(f"/proc/{d}").st_uid != UID:
                continue
            raw = open(f"/proc/{d}/stat").read()
            comm = raw[raw.index("(") + 1:raw.rindex(")")]
            f = raw[raw.rindex(")") + 2:].split()
            args = open(f"/proc/{d}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace").strip()
        except (OSError, ValueError):
            continue
        procs[pid] = {"comm": comm, "state": f[0], "ppid": int(f[1]),
                      "cpu": int(f[11]) + int(f[12]), "start": int(f[19]), "args": args}
    return procs


def children_map(procs):
    kids = {}
    for p, v in procs.items():
        kids.setdefault(v["ppid"], []).append(p)
    return kids


def tree(root, kids):
    out, stack = [root], [root]
    while stack:
        for c in kids.get(stack.pop(), []):
            out.append(c)
            stack.append(c)
    return out


def pss(pid):
    try:
        for line in open(f"/proc/{pid}/smaps_rollup"):
            if line.startswith("Pss:"):
                return int(line.split()[1]) * 1024
    except OSError:
        pass
    try:
        return int(open(f"/proc/{pid}/statm").read().split()[1]) * PAGE
    except OSError:
        return 0


def cpu_ticks(pids):
    total = 0
    for p in pids:
        try:
            f = open(f"/proc/{p}/stat").read()
            f = f[f.rindex(")") + 2:].split()
            total += int(f[11]) + int(f[12])
        except (OSError, ValueError):
            pass
    return total


# ---------- claude sessions ----------

def claude_meta(pid):
    try:
        return json.load(open(os.path.expanduser(f"~/.claude/sessions/{pid}.json")))
    except (OSError, ValueError):
        return None


def transcript_summary(session_id):
    paths = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session_id}.jsonl"))
    if not paths:
        return {}
    title, prompts = None, []
    try:
        for line in open(paths[0], errors="replace"):
            if '"ai-title"' in line or '"custom-title"' in line:
                try:
                    d = json.loads(line)
                    title = d.get("customTitle") or d.get("aiTitle") or title
                except ValueError:
                    pass
            elif '"type":"user"' in line and '"turnOrigin":"human"' in line:
                try:
                    c = json.loads(line)["message"]["content"]
                except (ValueError, KeyError, TypeError):
                    continue
                if isinstance(c, list):
                    c = " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
                c = " ".join(str(c).split())
                if c and not c.startswith("<"):
                    prompts.append(c)
    except OSError:
        return {}
    out = {"title": title, "prompts": len(prompts)}
    if prompts:
        out["first_prompt"] = prompts[0][:200]
        if len(prompts) > 1:
            out["last_prompt"] = prompts[-1][:200]
    return out


# ---------- tmux ----------

def tmux(*args):
    r = subprocess.run(["tmux", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def sessions():
    fmt = "#{session_name}\t#{session_created}\t#{session_activity}\t#{session_attached}"
    out = []
    for line in tmux("list-sessions", "-F", fmt).splitlines():
        name, created, activity, attached = line.split("\t")
        panes = []
        pfmt = "#{pane_id}\t#{pane_pid}\t#{pane_current_command}\t#{pane_current_path}"
        for pl in tmux("list-panes", "-s", "-t", f"={name}", "-F", pfmt).splitlines():
            pid_, ppid, cmd, path = pl.split("\t")
            panes.append({"id": pid_, "pid": int(ppid), "cmd": cmd, "cwd": path})
        out.append({"name": name, "created": int(created), "activity": int(activity),
                    "attached": int(attached), "panes": panes})
    return out


def pane_tail(pane_id, n=4):
    lines = [l.rstrip() for l in tmux("capture-pane", "-p", "-t", pane_id, "-S", "-60").splitlines()]
    return [l for l in lines if l.strip()][-n:]


def own_ancestors(procs):
    out, p = set(), os.getpid()
    while p in procs and p not in out:
        out.add(p)
        p = procs[p]["ppid"]
    return out


def assess(sess_list, min_age_h, describe=True):
    """Fill in age, memory, busy reasons and eligibility. Samples CPU once for all sessions."""
    procs = proc_table()
    kids = children_map(procs)
    mine = own_ancestors(procs)
    now = time.time()
    for s in sess_list:
        s["pids"] = sorted({p for pane in s["panes"] for p in tree(pane["pid"], kids) if p in procs})
    before = {s["name"]: cpu_ticks(s["pids"]) for s in sess_list}
    if sess_list:
        time.sleep(CPU_SAMPLE_S)
    after = {s["name"]: cpu_ticks(s["pids"]) for s in sess_list}

    for s in sess_list:
        s["age_h"] = (now - s["created"]) / 3600
        s["idle_h"] = (now - s["activity"]) / 3600
        s["pss"] = sum(pss(p) for p in s["pids"])
        busy = []
        if mine & set(s["pids"]):
            busy.append("contains the Claude session running this check")
        cpu = (after[s["name"]] - before[s["name"]]) / HZ / CPU_SAMPLE_S
        s["cpu"] = cpu
        if cpu > CPU_BUSY_FRACTION:
            busy.append(f"using {cpu * 100:.0f}% CPU")
        s["claude"] = []
        for pane in s["panes"]:
            ptree = tree(pane["pid"], kids)
            claudes = [p for p in ptree if p in procs and procs[p]["comm"] == "claude"]
            under_claude = set()
            for c in claudes:
                ctree = tree(c, kids)
                under_claude.update(ctree)
                meta = claude_meta(c) or {}
                status = meta.get("status")
                tools = [p for p in ctree[1:] if "shell-snapshots" in procs[p]["args"]]
                info = {"pid": c, "status": status, "cwd": meta.get("cwd"), "name": meta.get("name")}
                if describe and meta.get("sessionId"):
                    info.update(transcript_summary(meta["sessionId"]))
                s["claude"].append(info)
                if status not in (None, "idle"):
                    busy.append(f"Claude {c} status is '{status}'")
                if tools:
                    busy.append(f"Claude {c} has {len(tools)} running shell command(s)")
            others = [p for p in ptree if p in procs and p not in under_claude
                      and procs[p]["comm"] not in SHELLS]
            for p in others:
                busy.append(f"pane {pane['id']} runs '{procs[p]['args'][:60]}'")
            for p in ptree:
                if p in procs and p not in under_claude and procs[p]["state"] in ("R", "D"):
                    busy.append(f"process {p} in state {procs[p]['state']}")
            if describe:
                pane["tail"] = pane_tail(pane["id"])
        s["busy"] = sorted(set(busy))
        s["old_enough"] = s["age_h"] >= min_age_h
        s["eligible"] = s["old_enough"] and not s["busy"]
        del s["pids"]
    return sess_list


def outside_tmux_claudes(sess_list):
    procs = proc_table()
    kids = children_map(procs)
    in_tmux = set()
    for s in sess_list:
        for pane in s["panes"]:
            in_tmux.update(tree(pane["pid"], kids))
    out = [p for p, v in procs.items() if v["comm"] == "claude" and p not in in_tmux]
    return out, sum(pss(p) for p in out)


# ---------- strays: leftover process trees outside tmux and ssh logins ----------

def listening_ports():
    """Map socket inode -> 'tcp:PORT' for every listening TCP socket."""
    out = {}
    for fn, kind in (("/proc/net/tcp", "tcp"), ("/proc/net/tcp6", "tcp")):
        try:
            for line in open(fn).read().splitlines()[1:]:
                f = line.split()
                if f[3] == "0A":  # LISTEN
                    out[f[9]] = f"{kind}:{int(f[1].rsplit(':', 1)[1], 16)}"
        except OSError:
            pass
    return out


def tree_ports(pids, ports):
    found = set()
    for p in pids:
        try:
            for fd in os.listdir(f"/proc/{p}/fd"):
                try:
                    t = os.readlink(f"/proc/{p}/fd/{fd}")
                except OSError:
                    continue
                if t.startswith("socket:[") and t[8:-1] in ports:
                    found.add(ports[t[8:-1]])
        except OSError:
            pass
    return sorted(found)


def is_infra(v):
    c = v["comm"]
    return c in INFRA or c.startswith(INFRA_PREFIX)


def stray_roots(procs, kids, in_tmux, mine):
    """Roots of process trees that no tmux session, ssh login or per-user service owns."""
    def ancestors(p):
        seen = []
        while p in procs and p not in seen:
            seen.append(p)
            p = procs[p]["ppid"]
        return seen
    roots = []
    for pid, v in procs.items():
        if pid in in_tmux or pid in mine or is_infra(v):
            continue
        anc = ancestors(procs[pid]["ppid"]) if procs[pid]["ppid"] in procs else []
        if any(a in in_tmux or a in mine or procs[a]["comm"] in ("sshd", "tmux", "tmux: server") for a in anc):
            continue  # inside a tmux session, or an interactive ssh login
        if any(not is_infra(procs[a]) and a != pid for a in anc):
            continue  # not a root: an ancestor is itself a stray
        roots.append(pid)
    return roots


def assess_strays(min_age_h):
    procs = proc_table()
    kids = children_map(procs)
    mine = own_ancestors(procs)
    in_tmux = set()
    for s in sessions():
        for pane in s["panes"]:
            in_tmux.update(tree(pane["pid"], kids))
    # tmux servers and clients are infrastructure, handled by the session part.
    roots = stray_roots(procs, kids, in_tmux, mine)
    ports = listening_ports()
    uptime = float(open("/proc/uptime").read().split()[0])
    groups = []
    for r in roots:
        pids = tree(r, kids)
        groups.append({"pid": r, "pids": pids, "start": procs[r]["start"],
                       "age_h": (uptime - procs[r]["start"] / HZ) / 3600,
                       "args": procs[r]["args"] or f"[{procs[r]['comm']}]", "comm": procs[r]["comm"],
                       "parent": procs[procs[r]["ppid"]]["comm"] if procs[r]["ppid"] in procs else "init",
                       "ports": tree_ports(pids, ports)})
    before = {g_["pid"]: cpu_ticks(g_["pids"]) for g_ in groups}
    if groups:
        time.sleep(CPU_SAMPLE_S)
    for g_ in groups:
        procs2 = {p: procs[p] for p in g_["pids"] if p in procs}
        g_["pss"] = sum(pss(p) for p in g_["pids"])
        g_["n"] = len(g_["pids"])
        g_["cpu"] = (cpu_ticks(g_["pids"]) - before[g_["pid"]]) / HZ / CPU_SAMPLE_S
        try:
            g_["cwd"] = os.readlink(f"/proc/{g_['pid']}/cwd")
        except OSError:
            g_["cwd"] = None
        busy = []
        if g_["cpu"] > CPU_BUSY_FRACTION:
            busy.append(f"using {g_['cpu'] * 100:.0f}% CPU")
        for p, v in procs2.items():
            if v["state"] in ("R", "D"):
                busy.append(f"process {p} in state {v['state']}")
        g_["busy"] = sorted(set(busy))
        g_["old_enough"] = g_["age_h"] >= min_age_h
        g_["eligible"] = g_["old_enough"] and not g_["busy"]
        del g_["pids"]
    groups.sort(key=lambda x: -x["age_h"])
    return groups


# ---------- output ----------

def g(b):
    return f"{b / GiB:.2f} GiB"


def print_memory(m):
    if m is None:
        print("Memory: user slice not found at", SLICE)
        return
    print(f"Memory (user slice): non-cache {g(m['noncache'])}, total {g(m['current'])} "
          f"incl. {g(m['cache'])} reclaimable cache")
    print(f"  soft limit {SOFT_LIMIT_GIB:g} GiB (this skill), throttling at {g(m['high']) if m['high'] else 'none'}, "
          f"OOM kill at {g(m['max']) if m['max'] else 'none'}")
    over = m["noncache"] > m["soft"]
    print(f"  status: {'OVER soft limit by ' + g(m['noncache'] - m['soft']) if over else 'under soft limit'}")


def print_strays(strays, min_age):
    print(f"\nStray process trees (outside tmux and ssh logins): {len(strays)} using {g(sum(x['pss'] for x in strays))}")
    for x in strays:
        tag = "ELIGIBLE" if x["eligible"] else ("too young" if not x["old_enough"] else "ACTIVE")
        ports = f", LISTENS on {' '.join(x['ports'])}" if x["ports"] else ""
        print(f"[{tag}] pid {x['pid']}  age {x['age_h']:.1f} h, {x['n']} process(es), {g(x['pss'])}, "
              f"parent {x['parent']}{ports}")
        print(f"   cmd: {x['args'][:200]}")
        if x["cwd"]:
            print(f"   cwd: {x['cwd']}")
        for r in x["busy"]:
            print(f"   active: {r}")


def cmd_report(a):
    m = slice_memory()
    ss = assess(sessions(), a.min_age_hours)
    ss.sort(key=lambda s: s["created"])
    stray, stray_mem = outside_tmux_claudes(ss)
    strays = assess_strays(a.stray_min_age_hours)
    if a.json:
        json.dump({"memory": m, "min_age_hours": a.min_age_hours, "sessions": ss,
                   "claude_outside_tmux": {"pids": stray, "pss": stray_mem},
                   "strays": strays}, sys.stdout, indent=1)
        print()
        return 0
    print_memory(m)
    print(f"Claude processes outside tmux: {len(stray)} using {g(stray_mem)}")
    print_strays(strays, a.stray_min_age_hours)
    if not ss:
        print("\nNo tmux sessions.")
        return 0
    print(f"\n{len(ss)} tmux session(s), oldest first. Eligible = older than {a.min_age_hours:g} h and nothing active.")
    for s in ss:
        tag = "ELIGIBLE" if s["eligible"] else ("too young" if not s["old_enough"] else "ACTIVE")
        print(f"\n[{tag}] {s['name']}  age {s['age_h']:.1f} h, last output {s['idle_h']:.1f} h ago, "
              f"{g(s['pss'])}, {'attached' if s['attached'] else 'detached'}")
        for r in s["busy"]:
            print(f"   active: {r}")
        for c in s["claude"]:
            print(f"   claude pid {c['pid']} status={c['status']} cwd={c.get('cwd')}")
            for k in ("title", "first_prompt", "last_prompt"):
                if c.get(k):
                    print(f"     {k}: {c[k]}")
        for p in s["panes"]:
            print(f"   pane {p['id']} {p['cmd']} in {p['cwd']}")
            for l in p.get("tail", []):
                print(f"     | {l[:160]}")
    return 0


def cmd_kill(a):
    by_name = {s["name"]: s for s in sessions()}
    missing = [n for n in a.names if n not in by_name]
    for n in missing:
        print(f"SKIP {n}: no such tmux session")
    targets = assess([by_name[n] for n in a.names if n in by_name], a.min_age_hours, describe=False)
    before = slice_memory()
    procs = proc_table()
    kids = children_map(procs)
    rc = 0
    for s in targets:
        if not s["eligible"]:
            why = "; ".join(s["busy"]) or f"only {s['age_h']:.1f} h old"
            print(f"SKIP {s['name']}: no longer eligible ({why})")
            rc = 1
            continue
        pids = {p for pane in s["panes"] for p in tree(pane["pid"], kids)}
        subprocess.run(["tmux", "kill-session", "-t", f"={s['name']}"])
        deadline = time.time() + 10
        while time.time() < deadline and any(os.path.exists(f"/proc/{p}") for p in pids):
            time.sleep(0.5)
        left = [p for p in pids if os.path.exists(f"/proc/{p}")]
        for p in left:
            try:
                os.kill(p, signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                pass
        print(f"KILLED {s['name']} ({g(s['pss'])})" + (f", sent SIGTERM to {len(left)} leftover process(es)" if left else ""))
    after = slice_memory()
    if before and after:
        print(f"Non-cache memory: {g(before['noncache'])} -> {g(after['noncache'])}")
    return rc


def cmd_kill_strays(a):
    by_pid = {x["pid"]: x for x in assess_strays(a.stray_min_age_hours)}
    before = slice_memory()
    procs = proc_table()
    kids = children_map(procs)
    rc = 0
    for pid in a.pids:
        x = by_pid.get(pid)
        if x is None:
            print(f"SKIP {pid}: not a stray process tree (gone, or now inside tmux or an ssh login)")
            rc = 1
            continue
        if not x["eligible"]:
            why = "; ".join(x["busy"]) or f"only {x['age_h']:.1f} h old"
            print(f"SKIP {pid}: no longer eligible ({why})")
            rc = 1
            continue
        pids = tree(pid, kids)
        sig = signal.SIGKILL if a.force else signal.SIGTERM
        for p in reversed(pids):
            try:
                os.kill(p, sig)
            except (ProcessLookupError, PermissionError):
                pass
        deadline = time.time() + 5
        while time.time() < deadline and any(os.path.exists(f"/proc/{p}") for p in pids):
            time.sleep(0.5)
        left = [p for p in pids if os.path.exists(f"/proc/{p}") and open(f"/proc/{p}/stat").read().split(")")[-1].split()[0] != "Z"]
        print(f"KILLED {pid} ({x['args'][:80]}, {g(x['pss'])})" +
              (f"; {len(left)} process(es) survived {sig.name}, rerun with --force for SIGKILL" if left else ""))
    after = slice_memory()
    if before and after:
        print(f"Non-cache memory: {g(before['noncache'])} -> {g(after['noncache'])}")
    return rc


def cmd_check(a):
    m = slice_memory()
    # Only on machines that cap the user slice (the login node), so a laptop stays silent.
    if m and m["high"] and m["noncache"] > m["soft"]:
        print(f"WARNING: login-node memory for this user is {g(m['noncache'])} (soft limit {SOFT_LIMIT_GIB:g} GiB, "
              f"throttling at {g(m['high']) if m['high'] else '?'}). Tell the user and suggest the tmux-hygiene skill "
              f"to kill old idle tmux sessions and stray daemons.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report")
    r.add_argument("--json", action="store_true")
    k = sub.add_parser("kill")
    k.add_argument("names", nargs="+")
    ks = sub.add_parser("kill-strays")
    ks.add_argument("pids", nargs="+", type=int)
    ks.add_argument("--force", action="store_true", help="SIGKILL instead of SIGTERM")
    sub.add_parser("check")
    for p in (r, k):
        p.add_argument("--min-age-hours", type=float, default=48.0)
    for p in (r, k, ks):
        p.add_argument("--stray-min-age-hours", type=float, default=1.0)
    a = ap.parse_args()
    return {"report": cmd_report, "kill": cmd_kill, "kill-strays": cmd_kill_strays, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
