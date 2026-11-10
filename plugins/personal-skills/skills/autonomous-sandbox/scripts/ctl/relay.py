#!/usr/bin/env python3
"""Runs INSIDE the container (read-only). It forwards 127.0.0.1:3128 to the host proxy's Unix socket /sock/proxy.sock.

The container has its own network namespace that holds only loopback, so nothing outside the container can reach
this port. Every client inside sees a normal HTTP proxy (HTTPS_PROXY). The host proxy decides what is allowed out.
"""
import socket, threading

SOCK, ADDR = "/sock/proxy.sock", ("127.0.0.1", 3128)


def pipe(a, b):
    try:
        while True:
            d = a.recv(65536)
            if not d:
                break
            b.sendall(d)
    except OSError:
        pass
    finally:
        try:
            b.shutdown(socket.SHUT_WR)
        except OSError:
            pass


def handle(c):
    u = socket.socket(socket.AF_UNIX)
    try:
        u.connect(SOCK)
    except OSError:
        c.close()
        return
    t = threading.Thread(target=pipe, args=(u, c), daemon=True)
    t.start()
    pipe(c, u)
    t.join()
    c.close()
    u.close()


srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(ADDR)
srv.listen(256)
while True:
    conn, _ = srv.accept()
    threading.Thread(target=handle, args=(conn,), daemon=True).start()
