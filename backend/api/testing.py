"""Test adapter for the FastAPI application.

Provides a thin compatibility layer so tests can use
``app.test_client()`` / ``response.data`` against the FastAPI app.
"""

from __future__ import annotations

import json
from typing import Any, cast

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient


class _SyntheticResponse:
    """Small response object used when the client rejects a malformed URL."""

    def __init__(self, status_code: int, payload: dict[str, str]) -> None:
        self.status_code = status_code
        self.headers: dict[str, str] = {}
        self.content = json.dumps(payload).encode("utf-8")

    def json(self) -> dict[str, str]:
        return cast(dict[str, str], json.loads(self.content.decode("utf-8")))


class _TestClientResponse:
    """Minimal response adapter wrapping an httpx response."""

    def __init__(self, response) -> None:  # type: ignore[no-untyped-def]
        self._response = response

    @property
    def data(self) -> bytes:
        return bytes(self._response.content)

    def __getattr__(self, name: str):  # type: ignore[no-untyped-def]
        return getattr(self._response, name)


class _TestClient:
    """Minimal test client adapter for the FastAPI app."""

    def __init__(self, app: FastAPI) -> None:
        self._client = TestClient(app)

    def __enter__(self) -> _TestClient:
        self._client.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self._client.__exit__(exc_type, exc, tb)

    @staticmethod
    def _normalize_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(kwargs)
        content_type = normalized.pop("content_type", None)
        if isinstance(content_type, str):
            raw_headers = normalized.get("headers")
            headers = dict(cast(dict[str, str], raw_headers or {}))
            headers.setdefault("Content-Type", content_type)
            normalized["headers"] = headers
        return normalized

    def _request(self, method: str, *args, **kwargs):  # type: ignore[no-untyped-def]
        try:
            request_fn = cast(Any, self._client).request
            response: Any = request_fn(method, *args, **self._normalize_kwargs(kwargs))
        except httpx.InvalidURL as exc:
            payload = {"error": "Invalid input", "message": str(exc)}
            response = _SyntheticResponse(status_code=400, payload=payload)
        return _TestClientResponse(response)

    def get(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return self._request("GET", *args, **kwargs)

    def post(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return self._request("POST", *args, **kwargs)

    def delete(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return self._request("DELETE", *args, **kwargs)

    def put(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return self._request("PUT", *args, **kwargs)

    def options(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        return self._request("OPTIONS", *args, **kwargs)
