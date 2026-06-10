import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib import request

from openseeker_factory.backends import OpenAICompatibleChatBackend


class _ChatHandler(BaseHTTPRequestHandler):
    requests: list[dict] = []

    def do_POST(self) -> None:
        length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(length))
        self.__class__.requests.append(
            {
                "path": self.path,
                "authorization": self.headers.get("Authorization"),
                "body": body,
            }
        )
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "question": "Teacher drafted question?",
                                "difficulty": "hard",
                            }
                        )
                    }
                }
            ]
        }
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format: str, *args) -> None:
        return


def test_openai_compatible_backend_posts_chat_request_and_parses_json():
    _ChatHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _ChatHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        backend = OpenAICompatibleChatBackend(
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            model="fake-model",
            api_key="test-key",
        )

        draft = backend.complete_json(
            [{"role": "user", "content": "Draft one synthetic task."}]
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert draft == {"question": "Teacher drafted question?", "difficulty": "hard"}
    assert _ChatHandler.requests[0]["path"] == "/v1/chat/completions"
    assert _ChatHandler.requests[0]["authorization"] == "Bearer test-key"
    assert _ChatHandler.requests[0]["body"]["model"] == "fake-model"


def test_openai_compatible_backend_strips_api_key_line_endings():
    _ChatHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _ChatHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        backend = OpenAICompatibleChatBackend(
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            model="fake-model",
            api_key="test-key\r\n",
        )

        backend.complete_json([{"role": "user", "content": "Draft one task."}])
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert _ChatHandler.requests[0]["authorization"] == "Bearer test-key"


def test_openai_compatible_backend_wraps_timeout_without_leaking_key(monkeypatch):
    class TimeoutResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            raise TimeoutError("raw timeout")

    def fake_urlopen(req, timeout):
        return TimeoutResponse()

    monkeypatch.setattr(request, "urlopen", fake_urlopen)
    backend = OpenAICompatibleChatBackend(
        base_url="https://api.example.test/v1",
        model="fake-model",
        api_key="test-secret",
    )

    try:
        backend.complete_json([{"role": "user", "content": "Draft one task."}])
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected RuntimeError")

    assert "timed out" in message
    assert "test-secret" not in message
