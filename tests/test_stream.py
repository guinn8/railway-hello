# tests/test_stream.py
import time
from starlette.testclient import TestClient
from main import app

def test_stream_demo_fast():
    with TestClient(app) as client:
        t0 = time.perf_counter()
        with client.stream("GET", "/stream-demo") as resp:
            data = resp.read().decode()
        dt = time.perf_counter() - t0
        assert "pong" in data
        assert dt < 1.0, f"stream too slow: {dt:.2f}s"
