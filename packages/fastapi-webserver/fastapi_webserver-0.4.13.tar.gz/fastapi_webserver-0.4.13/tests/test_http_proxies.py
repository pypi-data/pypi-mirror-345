import tempfile
import unittest
from pathlib import Path

from commons.media import mimetypes
from fastapi.testclient import TestClient

TEMP_FOLDER: Path = Path(tempfile.gettempdir())


class TestProxies(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        # Execute a code after all tests
        import os
        os.remove(TEMP_FOLDER / "cache.db")

    @staticmethod
    def client() -> TestClient:
        from webserver import app, settings, core
        from webserver.http import proxies

        settings.RESOURCES_FOLDER = TEMP_FOLDER
        core._setup_databases()
        app.include_router(proxies.gravatar_router)
        app.include_router(proxies.giphy_router)
        return TestClient(app)

    def test_gravatar(self):
        client = self.client()
        response = client.get("/proxy/avatar/abc")
        assert response.status_code == 200
        assert response.headers["X-Cache"] == "MISS"
        assert response.headers["Age"] == "0"
        assert response.headers["Content-Type"] == mimetypes.IMAGE_WEBP
        assert response.headers["Content-Source"] == "Gravatar"
        assert response.headers["Content-Length"] == "492"
        assert response.headers["Content-Disposition"] == 'inline; filename="Gravatar-abc+32.webp"'
        assert client.get("/proxy/avatar/").status_code == 404

    def test_giphy(self):
        client = self.client()
        response = client.get("/proxy/gif/abc")
        assert response.status_code == 200
        assert response.headers["X-Cache"] == "MISS"
        assert response.headers["Age"] == "0"
        assert response.headers["Content-Type"] == mimetypes.IMAGE_GIF
        assert response.headers["Content-Source"] == "Giphy"
        assert response.headers["Content-Length"] == "239321"
        assert response.headers["Content-Disposition"] == 'inline; filename="Giphy-abc.gif"'
        assert client.get("/proxy/gif/").status_code == 404