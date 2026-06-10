from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib import error, request


class ChatBackend(Protocol):
    name: str

    def complete_json(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class OpenAICompatibleChatBackend:
    base_url: str
    model: str
    api_key: str
    timeout_s: float = 30.0
    name: str = "openai-compatible"

    def __post_init__(self) -> None:
        self.api_key = self.api_key.strip()

    def complete_json(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.base_url.rstrip("/") + "/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read()
        except error.URLError as exc:
            raise RuntimeError(f"failed to call OpenAI-compatible backend: {exc}") from exc
        except TimeoutError as exc:
            raise RuntimeError(
                "failed to call OpenAI-compatible backend: request timed out"
            ) from exc
        except ValueError as exc:
            raise RuntimeError(
                "failed to call OpenAI-compatible backend: invalid request headers"
            ) from exc

        response = json.loads(raw.decode("utf-8"))
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("backend response did not contain chat completion content") from exc

        if isinstance(content, dict):
            return content
        if isinstance(content, str):
            return json.loads(content)
        raise ValueError("backend content must be JSON string or object")


def build_chat_backend(
    *,
    backend: str | None,
    base_url: str | None,
    model: str | None,
    api_key_env: str = "OPENAI_API_KEY",
    timeout_s: float = 30.0,
) -> ChatBackend | None:
    if backend in {None, "", "none"}:
        return None
    if backend != "openai-compatible":
        raise ValueError("backend must be openai-compatible or none")
    if not base_url:
        raise ValueError("teacher backend base_url is required")
    if not model:
        raise ValueError("teacher backend model is required")

    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise ValueError(f"environment variable {api_key_env!r} is required")

    return OpenAICompatibleChatBackend(
        base_url=base_url,
        model=model,
        api_key=api_key,
        timeout_s=timeout_s,
    )
