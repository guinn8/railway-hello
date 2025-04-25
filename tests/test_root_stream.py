# tests/test_root_stream.py
import time, httpx
from starlette.testclient import TestClient
from main import app

def test_root_header_stream_fast():
    with TestClient(app) as client:
        t0 = time.perf_counter()
        with client.stream("GET", "/", headers={"X-Stream": "1"}) as resp:
            first_chunk = resp.read()          # all html but arrives in one go under stub
        dt = time.perf_counter() - t0
        assert first_chunk.startswith(b"<!doctype html>")
        assert dt < 0.3, f"first byte too slow: {dt:.3f}s"

def test_root_buffer_equals_stream():
    with TestClient(app) as client:
        html_buf = client.get("/").text
        html_stream = client.get("/", headers={"X-Stream": "1"}).text
        assert html_buf == html_stream
