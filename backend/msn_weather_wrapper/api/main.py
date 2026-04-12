"""FastAPI application entrypoint for the MSN Weather Wrapper."""

from __future__ import annotations

import json
import re
import time
import uuid
from collections import defaultdict, deque
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from threading import Lock
from typing import Any, cast

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from msn_weather_wrapper.api.config import (
    DEBUG,
    RATE_LIMIT_GLOBAL,
    RATE_LIMIT_PER_IP,
    TESTING,
    get_cors_origins,
    get_secret_key,
)
from msn_weather_wrapper.api.routers.health import router as health_router
from msn_weather_wrapper.api.routers.weather import router as weather_router
from msn_weather_wrapper.api.services import close_client, logger


class _InMemoryRateLimiter:
    """Simple process-local rate limiter for API requests."""

    def __init__(self, per_ip_limit: str, global_limit: str) -> None:
        self.per_ip_max, self.per_ip_window = self._parse_limit(per_ip_limit, default_window=60)
        self.global_max, self.global_window = self._parse_limit(global_limit, default_window=3600)
        self._ip_requests: dict[str, deque[float]] = defaultdict(deque)
        self._global_requests: deque[float] = deque()
        self._lock = Lock()

    @staticmethod
    def _parse_limit(limit_value: str, *, default_window: int) -> tuple[int, int]:
        match = re.match(r"^\s*(\d+)\s+per\s+(minute|hour)\s*$", limit_value, re.IGNORECASE)
        if not match:
            return int(limit_value), default_window

        count = int(match.group(1))
        window_label = match.group(2).lower()
        return count, 60 if window_label == "minute" else 3600

    @staticmethod
    def _trim(bucket: deque[float], now: float, window: int) -> None:
        while bucket and now - bucket[0] >= window:
            bucket.popleft()

    def check(self, request: Request) -> int | None:
        """Return a retry-after value when the request should be limited."""
        client_host = request.client.host if request.client else "anonymous"
        now = time.monotonic()

        with self._lock:
            ip_bucket = self._ip_requests[client_host]
            self._trim(ip_bucket, now, self.per_ip_window)
            self._trim(self._global_requests, now, self.global_window)

            if len(ip_bucket) >= self.per_ip_max:
                return max(1, int(self.per_ip_window - (now - ip_bucket[0])))
            if len(self._global_requests) >= self.global_max:
                return max(1, int(self.global_window - (now - self._global_requests[0])))

            ip_bucket.append(now)
            self._global_requests.append(now)

        return None


rate_limiter = _InMemoryRateLimiter(RATE_LIMIT_PER_IP, RATE_LIMIT_GLOBAL)


class _SyntheticResponse:
    """Small response object used when the client rejects a malformed URL."""

    def __init__(self, status_code: int, payload: dict[str, str]) -> None:
        self.status_code = status_code
        self.headers: dict[str, str] = {}
        self.content = json.dumps(payload).encode("utf-8")

    def json(self) -> dict[str, str]:
        return cast(dict[str, str], json.loads(self.content.decode("utf-8")))


class _FlaskStyleResponse:
    """Minimal response adapter for legacy Flask-style tests."""

    def __init__(self, response) -> None:  # type: ignore[no-untyped-def]
        self._response = response

    @property
    def data(self) -> bytes:
        return bytes(self._response.content)

    def __getattr__(self, name: str):  # type: ignore[no-untyped-def]
        return getattr(self._response, name)


class _FlaskStyleTestClient:
    """Minimal client adapter matching the old Flask test API."""

    def __init__(self, app: FastAPI) -> None:
        self._client = TestClient(app)

    def __enter__(self) -> _FlaskStyleTestClient:
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
        return _FlaskStyleResponse(response)

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


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Clean up shared resources on shutdown."""
    yield
    close_client()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="MSN Weather Wrapper API",
        description=(
            "A FastAPI wrapper for MSN Weather providing weather data, forecasts, "
            "and location search functionality."
        ),
        version="1.0.0",
        docs_url="/apidocs",
        openapi_url="/apispec.json",
        redoc_url=None,
        lifespan=lifespan,
        contact={
            "name": "API Support",
            "url": "https://github.com/jim-wyatt/msn-weather-wrapper",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        openapi_tags=[
            {"name": "health", "description": "Health check and readiness endpoints"},
            {"name": "weather", "description": "Weather data and search history endpoints"},
        ],
    )

    app.state.testing = TESTING
    app.config = {"TESTING": TESTING}  # type: ignore[attr-defined]
    app.test_client = lambda: _FlaskStyleTestClient(app)  # type: ignore[attr-defined]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=get_secret_key(),
        same_site="lax",
        https_only=not DEBUG,
    )

    @app.middleware("http")
    async def add_request_context(request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            ip=request.client.host if request.client else None,
        )

        if request.method != "OPTIONS" and not app.state.testing:
            retry_after = rate_limiter.check(request)
            if retry_after is not None:
                response = JSONResponse(
                    content={
                        "error": "Rate limit exceeded",
                        "message": "Too many requests. Please try again later.",
                        "retry_after": str(retry_after),
                    },
                    status_code=429,
                )
                response.headers["Retry-After"] = str(retry_after)
                response.headers["X-Request-ID"] = request_id
                return response

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed",
            request_id=request_id,
            status_code=response.status_code,
            path=request.url.path,
        )
        return response

    app.include_router(health_router, prefix="/api")
    app.include_router(weather_router, prefix="/api")
    return app


app = create_app()
