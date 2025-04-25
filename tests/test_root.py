# tests/test_root.py
from starlette.testclient import TestClient
from main import app

def test_root_route_ok():
    with TestClient(app) as c:
        r = c.get("/")
        assert r.status_code == 200
        assert "<html" in r.text.lower()
