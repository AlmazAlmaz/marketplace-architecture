import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from services.orders.app import create_server


class HealthEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server("127.0.0.1", 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def test_health_returns_200_and_json(self) -> None:
        with urlopen(f"{self.base_url}/health", timeout=2) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get_content_type(), "application/json")
            self.assertEqual(json.load(response), {"status": "ok", "service": "orders"})

    def test_health_accepts_query_string(self) -> None:
        with urlopen(f"{self.base_url}/health?probe=docker", timeout=2) as response:
            self.assertEqual(response.status, 200)

    def test_business_endpoints_are_not_implemented(self) -> None:
        for path in ("/orders", "/payments", "/users", "/products"):
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as error:
                    urlopen(f"{self.base_url}{path}", timeout=2)
                with error.exception as response:
                    self.assertEqual(response.code, 404)
                    self.assertEqual(json.load(response), {"error": "not_found"})

    def test_server_does_not_expose_files(self) -> None:
        for path in ("/", "/app.py", "/../../README.md", "/health/other"):
            with self.subTest(path=path):
                with self.assertRaises(HTTPError) as error:
                    urlopen(f"{self.base_url}{path}", timeout=2)
                with error.exception as response:
                    self.assertEqual(response.code, 404)


if __name__ == "__main__":
    unittest.main()
