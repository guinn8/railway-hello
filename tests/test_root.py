# tests/test_root.py
import time
from starlette.testclient import TestClient
from main import app

def test_root_stream_fast():
    with TestClient(app) as client:
        t0 = time.perf_counter()
        with client.stream("GET", "/") as resp:
            html = resp.read()
        dt = time.perf_counter() - t0
        assert html.lower().startswith(b"<!doctype html")
        assert dt < 0.3, f"stream too slow: {dt:.3f}s"
