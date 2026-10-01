"""Orders service bootstrap. No marketplace business logic is implemented."""

import json
import os
import signal
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if urlsplit(self.path).path == "/health":
            status = HTTPStatus.OK
            payload = {"status": "ok", "service": "orders"}
        else:
            status = HTTPStatus.NOT_FOUND
            payload = {"error": "not_found"}

        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def create_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), HealthHandler)


def stop(_signum: int, _frame: object) -> None:
    raise SystemExit(0)


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    if not 1 <= port <= 65535:
        raise ValueError("PORT must be between 1 and 65535")

    signal.signal(signal.SIGTERM, stop)
    with create_server("0.0.0.0", port) as server:
        print(f"Orders health endpoint listening on port {port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
