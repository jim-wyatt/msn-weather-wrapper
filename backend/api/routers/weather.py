"""Weather and recent-search routes for the FastAPI service."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from backend.api.config import MAX_CITY_LENGTH, MAX_COUNTRY_LENGTH
from backend.api.services import (
    add_to_recent_searches,
    build_weather_payload,
    clear_recent_search_history,
    get_cached_weather,
    get_client,
    get_minute_bucket,
    get_recent_search_history,
    logger,
    validate_input,
)
from backend.exceptions import LocationNotFoundError, UpstreamError, WeatherError

router = APIRouter(tags=["weather"])


def _get_request_id(request: Request) -> str | None:
    value = getattr(request.state, "request_id", None)
    return str(value) if value is not None else None


def _invalid_request(
    message: str,
    *,
    error: str = "Invalid request",
    status_code: int = 400,
) -> JSONResponse:
    return JSONResponse(content={"error": error, "message": message}, status_code=status_code)


def _handle_weather_lookup(request: Request, city: Any, country: Any) -> JSONResponse:
    if not city or not country:
        logger.warning(
            "missing_parameters",
            request_id=_get_request_id(request),
            city=city,
            country=country,
        )
        return _invalid_request(
            "Both 'city' and 'country' parameters are required",
            error="Missing required parameters",
        )

    city, city_error = validate_input(city, "city", MAX_CITY_LENGTH)
    if city_error:
        logger.warning(
            "invalid_city",
            request_id=_get_request_id(request),
            error=city_error,
        )
        return _invalid_request(city_error, error="Invalid input")

    country, country_error = validate_input(country, "country", MAX_COUNTRY_LENGTH)
    if country_error:
        logger.warning(
            "invalid_country",
            request_id=_get_request_id(request),
            error=country_error,
        )
        return _invalid_request(country_error, error="Invalid input")

    logger.info(
        "fetching_weather",
        request_id=_get_request_id(request),
        city=city,
        country=country,
    )

    weather_data, status_code = get_cached_weather(city, country, get_minute_bucket())
    if status_code == 200:
        add_to_recent_searches(request, city, country)
        logger.info(
            "weather_fetched_successfully",
            request_id=_get_request_id(request),
            city=city,
            country=country,
            cached=True,
        )
    else:
        logger.error(
            "weather_fetch_failed",
            request_id=_get_request_id(request),
            city=city,
            country=country,
            status_code=status_code,
        )

    return JSONResponse(content=weather_data, status_code=status_code)


@router.get("/v1/weather")
async def get_weather(
    request: Request,
    city: str | None = None,
    country: str | None = None,
) -> JSONResponse:
    """Get weather data for a city and country."""
    return _handle_weather_lookup(request, city, country)


@router.post("/v1/weather")
async def get_weather_post(request: Request) -> JSONResponse:
    """Get weather data from a JSON request body."""
    content_type = request.headers.get("content-type", "")
    normalized_content_type = content_type.lower().split(";", maxsplit=1)[0].strip()
    if content_type and (
        "," in content_type or normalized_content_type not in {"", "application/json"}
    ):
        return _invalid_request(
            "Request body must be valid JSON",
            status_code=415,
        )

    try:
        data = await request.json()
    except Exception as exc:
        logger.warning(
            "invalid_json",
            request_id=getattr(request.state, "request_id", None),
            error=str(exc),
        )
        return _invalid_request("Request body must be valid JSON")

    if not data or not isinstance(data, dict):
        return _invalid_request("Request body must be a JSON object")

    return _handle_weather_lookup(request, data.get("city"), data.get("country"))


@router.options("/v1/weather", status_code=204)
async def weather_options() -> Response:
    """Handle CORS preflight requests."""
    return Response(status_code=204)


@router.get("/v1/weather/coordinates")
async def get_weather_by_coordinates(
    request: Request,
    lat: str | None = None,
    lon: str | None = None,
) -> JSONResponse:
    """Get weather data by geographic coordinates."""
    if not lat or not lon:
        return _invalid_request(
            "Both 'lat' and 'lon' parameters are required",
            error="Missing required parameters",
        )

    try:
        latitude = float(lat)
        longitude = float(lon)

        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
    except ValueError as exc:
        return _invalid_request(str(exc), error="Invalid coordinates")

    try:
        weather = get_client().get_weather_by_coordinates(latitude, longitude)
        payload = build_weather_payload(weather)
        return JSONResponse(content=payload, status_code=200)
    except LocationNotFoundError as exc:
        return _invalid_request(str(exc), error="Location not found", status_code=404)
    except UpstreamError as exc:
        return _invalid_request(str(exc), error="Upstream service error", status_code=502)
    except WeatherError as exc:
        return _invalid_request(str(exc), error="Weather service error", status_code=500)
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.error(
            "unexpected_error",
            request_id=_get_request_id(request),
            lat=lat,
            lon=lon,
            error=str(exc),
        )
        return _invalid_request(str(exc), error="Internal server error", status_code=500)


@router.get("/v1/recent-searches")
async def get_recent_searches(request: Request) -> dict[str, list[dict[str, str]]]:
    """Return recent searches for the current session."""
    return {"recent_searches": get_recent_search_history(request)}


@router.delete("/v1/recent-searches")
async def clear_recent_searches(request: Request) -> dict[str, str]:
    """Clear recent searches for the current session."""
    clear_recent_search_history(request)
    return {"message": "Recent searches cleared"}
