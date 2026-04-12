"""FastAPI application package for the MSN Weather Wrapper."""

from msn_weather_wrapper.api.config import CACHE_DURATION_MINUTES, CACHE_SIZE
from msn_weather_wrapper.api.main import app, create_app
from msn_weather_wrapper.api.services import get_cached_weather, get_client, validate_input

__all__ = [
    "app",
    "create_app",
    "get_cached_weather",
    "get_client",
    "validate_input",
    "CACHE_SIZE",
    "CACHE_DURATION_MINUTES",
]
