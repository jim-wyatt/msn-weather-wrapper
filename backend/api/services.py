"""Shared service helpers for the FastAPI weather API."""

from __future__ import annotations

import os
import re
import uuid
from collections import deque
from datetime import datetime
from functools import lru_cache
from typing import Any, cast

import structlog
from fastapi import Request

from backend import Location, WeatherClient
from backend.api.config import (
    CACHE_DURATION_MINUTES,
    CACHE_SIZE,
    MAX_CITY_LENGTH,
    MAX_COUNTRY_LENGTH,
)
from backend.exceptions import (
    LocationNotFoundError,
    ParsingError,
    UpstreamError,
    WeatherError,
)
from backend.models import WeatherData

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

VALID_NAME_PATTERN = re.compile(
    r"^[a-zA-Z\s\-\.,àáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ðА-Яа-яЁё\u4e00-\u9fff\u0600-\u06FF]+$",
    re.UNICODE,
)

recent_searches: dict[str, deque[dict[str, str]]] = {}
_weather_client: WeatherClient | None = None


def validate_input(
    value: str | None, field_name: str, max_length: int
) -> tuple[str | None, str | None]:
    """Validate and sanitize user input."""
    if not isinstance(value, str):
        return None, f"{field_name} must be a string"

    value = value.strip()
    if not value:
        return None, f"{field_name} cannot be empty or only whitespace"

    if len(value) > max_length:
        return None, f"{field_name} exceeds maximum length of {max_length} characters"

    if not VALID_NAME_PATTERN.match(value):
        return None, f"{field_name} contains invalid characters"

    return value, None


def get_client() -> WeatherClient:
    """Get or create the shared weather client instance."""
    global _weather_client

    if _weather_client is None:
        timeout = int(os.getenv("REQUEST_TIMEOUT", "15"))
        _weather_client = WeatherClient(timeout=timeout)

    return _weather_client


def close_client() -> None:
    """Close the shared weather client if it exists."""
    global _weather_client

    if _weather_client is not None:
        _weather_client.close()
        _weather_client = None


def build_weather_payload(weather: WeatherData) -> dict[str, Any]:
    """Serialize the weather model into an API response payload."""
    return weather.model_dump()


@lru_cache(maxsize=CACHE_SIZE)
def get_cached_weather(city: str, country: str, minute_bucket: int) -> tuple[dict[str, Any], int]:
    """Get weather with time-bucketed caching."""
    del minute_bucket  # Used only as cache key entropy.

    try:
        location = Location(city=city, country=country, latitude=None, longitude=None)
        weather = get_client().get_weather(location)
        return build_weather_payload(weather), 200
    except LocationNotFoundError as exc:
        logger.warning("location_not_found", city=city, country=country, error=str(exc))
        return {
            "error": "Location not found",
            "message": "The requested location could not be found.",
        }, 404
    except UpstreamError as exc:
        logger.error("upstream_error", city=city, country=country, error=str(exc))
        return {
            "error": "Upstream service error",
            "message": "Failed to fetch weather data from the upstream service.",
        }, 502
    except ParsingError as exc:
        logger.error("parsing_error", city=city, country=country, error=str(exc))
        return {"error": "Data parsing error", "message": "Failed to parse weather data."}, 500
    except WeatherError as exc:
        logger.error("weather_error", city=city, country=country, error=str(exc))
        return {
            "error": "Weather service error",
            "message": "The weather service encountered an error.",
        }, 500
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.error("unexpected_error", city=city, country=country, error=str(exc))
        return {"error": "Internal server error", "message": "An unexpected error occurred."}, 500


def get_minute_bucket(now: datetime | None = None) -> int:
    """Return the active cache bucket."""
    current_time = now or datetime.now()
    return current_time.minute // CACHE_DURATION_MINUTES if CACHE_DURATION_MINUTES > 0 else 0


def add_to_recent_searches(request: Request, city: str, country: str) -> None:
    """Store a location in the current session's recent-searches list."""
    session_id = cast(str | None, request.session.get("id"))
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["id"] = session_id

    if session_id not in recent_searches:
        recent_searches[session_id] = deque(maxlen=10)

    search_entry = {"city": city, "country": country}
    searches = recent_searches[session_id]
    if search_entry in searches:
        searches.remove(search_entry)
    searches.appendleft(search_entry)


def get_recent_search_history(request: Request) -> list[dict[str, str]]:
    """Return the current session's recent searches."""
    session_id = cast(str | None, request.session.get("id"))
    if not session_id or session_id not in recent_searches:
        return []
    return list(recent_searches[session_id])


def clear_recent_search_history(request: Request) -> None:
    """Delete the current session's recent-searches list."""
    session_id = cast(str | None, request.session.get("id"))
    if session_id and session_id in recent_searches:
        del recent_searches[session_id]


__all__ = [
    "CACHE_DURATION_MINUTES",
    "CACHE_SIZE",
    "MAX_CITY_LENGTH",
    "MAX_COUNTRY_LENGTH",
    "add_to_recent_searches",
    "build_weather_payload",
    "clear_recent_search_history",
    "close_client",
    "get_cached_weather",
    "get_client",
    "get_minute_bucket",
    "get_recent_search_history",
    "logger",
    "recent_searches",
    "validate_input",
]
