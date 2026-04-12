"""Compatibility entrypoint for the FastAPI application."""

from __future__ import annotations

import uvicorn

from backend.api import (
    CACHE_DURATION_MINUTES,
    CACHE_SIZE,
    app,
    get_cached_weather,
    get_client,
    validate_input,
)
from backend.api.config import DEBUG, HOST, PORT
from backend.api.services import datetime

__all__ = [
    "app",
    "get_client",
    "get_cached_weather",
    "validate_input",
    "CACHE_SIZE",
    "CACHE_DURATION_MINUTES",
    "datetime",
]


if __name__ == "__main__":
    uvicorn.run("api:app", host=HOST, port=PORT, reload=DEBUG)
