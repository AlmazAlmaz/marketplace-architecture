"""Container health probe using only the Python standard library."""

import json
import os
from urllib.request import urlopen


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    with urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as response:
        if response.status != 200:
            raise SystemExit("Health endpoint did not return 200")
        if json.load(response) != {"status": "ok", "service": "orders"}:
            raise SystemExit("Unexpected health response")


if __name__ == "__main__":
    main()
