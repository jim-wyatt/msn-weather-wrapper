"""FastAPI application package for the MSN Weather Wrapper."""

from backend.api.config import CACHE_DURATION_MINUTES, CACHE_SIZE
from backend.api.main import app, create_app
from backend.api.services import get_cached_weather, get_client, validate_input

__all__ = [
    "app",
    "create_app",
    "get_cached_weather",
    "get_client",
    "validate_input",
    "CACHE_SIZE",
    "CACHE_DURATION_MINUTES",
]
