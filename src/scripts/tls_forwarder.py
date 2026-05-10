"""TLS-terminating TCP forwarder.

Listens for HTTPS connections on a configured port, terminates TLS using a
server certificate and key, and forwards the decrypted byte stream to a plain
HTTP upstream. The forwarder is intentionally minimal: a few dozen lines of
the Python standard library, no third-party dependencies. NFR-002 requires
HTTPS on port 8443 alongside Django's runserver on 8000; rather than swap
runserver for a TLS-capable replacement, this script terminates TLS and hands
the unwrapped bytes to runserver via 127.0.0.1.

Usage:
    python tls_forwarder.py LISTEN_PORT UPSTREAM_HOST UPSTREAM_PORT CERT KEY
"""

from __future__ import annotations

import socket
import socketserver
import ssl
import sys
import threading
import time


# Buffer size for the byte-shovel between client and upstream sockets.
# 4 KiB matches the typical kernel pipe buffer chunking and is large enough
# that small HTTP request/response messages copy in one or two recv()s.
_BUFFER_SIZE = 4096

# Total wall-clock budget for the upstream connection retry loop. The
# forwarder is started before runserver in startup.sh, so the first few
# accepted connections may race the runserver bind. After this many seconds
# the connection attempt gives up and the client sees a 502-equivalent close.
_UPSTREAM_CONNECT_DEADLINE_SECONDS = 5.0

# Sleep between upstream connection retries when ECONNREFUSED is seen.
_UPSTREAM_RETRY_SLEEP_SECONDS = 0.1


class _TLSForwarder(socketserver.ThreadingTCPServer):
    """Threaded TCP server that wraps each accepted socket in TLS.

    The standard ``ThreadingTCPServer`` accepts plain sockets and dispatches
    them to handlers. Overriding ``get_request`` is the documented hook for
    wrapping each accepted socket; this is preferred over wrapping the
    listening socket because the TLS handshake must run per-connection.
    """

    allow_reuse_address = True
    daemon_threads = True

    def __init__(
        self,
        server_address: tuple[str, int],
        RequestHandlerClass: type[socketserver.BaseRequestHandler],
        ssl_context: ssl.SSLContext,
        upstream_host: str,
        upstream_port: int,
    ) -> None:
        super().__init__(server_address, RequestHandlerClass)
        self.ssl_context = ssl_context
        self.upstream_host = upstream_host
        self.upstream_port = upstream_port

    def get_request(self) -> tuple[ssl.SSLSocket, tuple[str, int]]:
        sock, addr = super().get_request()
        try:
            tls_sock = self.ssl_context.wrap_socket(sock, server_side=True)
        except (ssl.SSLError, OSError):
            sock.close()
            raise
        return tls_sock, addr


class _ForwardHandler(socketserver.BaseRequestHandler):
    """Pump bytes between the TLS-terminated client and a plain HTTP upstream."""

    server: _TLSForwarder

    def handle(self) -> None:
        upstream = self._connect_upstream()
        if upstream is None:
            self.request.close()
            return
        try:
            forward_thread = threading.Thread(
                target=self._copy,
                args=(self.request, upstream),
                daemon=True,
            )
            forward_thread.start()
            self._copy(upstream, self.request)
            forward_thread.join()
        finally:
            upstream.close()

    def _connect_upstream(self) -> socket.socket | None:
        deadline = time.monotonic() + _UPSTREAM_CONNECT_DEADLINE_SECONDS
        while True:
            try:
                return socket.create_connection(
                    (self.server.upstream_host, self.server.upstream_port),
                    timeout=2.0,
                )
            except (ConnectionRefusedError, OSError):
                if time.monotonic() >= deadline:
                    return None
                time.sleep(_UPSTREAM_RETRY_SLEEP_SECONDS)

    @staticmethod
    def _copy(src: socket.socket, dst: socket.socket) -> None:
        try:
            while True:
                data = src.recv(_BUFFER_SIZE)
                if not data:
                    break
                dst.sendall(data)
        except (OSError, ssl.SSLError):
            # Either side may close mid-transfer; both directions converge on
            # close() in the surrounding handle()/finally pair.
            pass


def main(argv: list[str]) -> int:
    if len(argv) != 6:
        print(
            "usage: tls_forwarder.py LISTEN_PORT UPSTREAM_HOST UPSTREAM_PORT "
            "CERT KEY",
            file=sys.stderr,
        )
        return 2
    listen_port = int(argv[1])
    upstream_host = argv[2]
    upstream_port = int(argv[3])
    cert_path = argv[4]
    key_path = argv[5]

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    server = _TLSForwarder(
        ("0.0.0.0", listen_port),
        _ForwardHandler,
        ssl_context,
        upstream_host,
        upstream_port,
    )
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
