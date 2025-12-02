"""Flask API for MSN Weather Wrapper."""

import re
import uuid
from collections import deque
from datetime import datetime
from functools import lru_cache
from typing import Any

import structlog
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from msn_weather_wrapper import Location, WeatherClient

# Configure structured logging
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

app = Flask(__name__)
app.secret_key = "msn-weather-secret-key-change-in-production"  # For session management
CORS(app, supports_credentials=True)  # Enable CORS for React frontend

# Configure rate limiting (in-memory storage, no Redis needed)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)

# In-memory storage for recent searches (per session)
# In production, consider using Redis or a database
recent_searches: dict[str, deque[dict[str, str]]] = {}

# Input validation constants
MAX_CITY_LENGTH = 100
MAX_COUNTRY_LENGTH = 100
# Allow letters (including international), spaces, hyphens, apostrophes, periods, and commas
# but not dangerous patterns like semicolons, backticks, angle brackets, etc.
VALID_NAME_PATTERN = re.compile(
    r"^[a-zA-Z\s\-\.,'àáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ðА-Яа-яЁё\u4e00-\u9fff\u0600-\u06FF]+$",
    re.UNICODE,
)


def validate_input(
    value: str | None, field_name: str, max_length: int
) -> tuple[str | None, str | None]:
    """Validate and sanitize input strings.

    Args:
        value: Input value to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length

    Returns:
        Tuple of (sanitized_value, error_message)
        error_message is None if validation passes
        sanitized_value is None if validation fails
    """
    # Check type first (before checking if value exists, since None is not a string)
    if not isinstance(value, str):
        return None, f"{field_name} must be a string"

    # Strip whitespace
    value = value.strip()

    # Check if empty after stripping
    if not value:
        return None, f"{field_name} cannot be empty or only whitespace"

    # Check length
    if len(value) > max_length:
        return None, f"{field_name} exceeds maximum length of {max_length} characters"

    # Check for valid characters (letters, numbers, spaces, basic punctuation)
    # Allow international characters for city/country names
    if not VALID_NAME_PATTERN.match(value):
        return None, f"{field_name} contains invalid characters"

    return value, None


def get_client() -> WeatherClient:
    """Get or create a weather client instance."""
    if not hasattr(app, "weather_client"):
        app.weather_client = WeatherClient(timeout=15)
    return app.weather_client


@lru_cache(maxsize=1000)
def get_cached_weather(
    city: str, country: str, minute_bucket: int
) -> tuple[dict[str, str | float | int], int]:
    """Get weather with 5-minute caching.

    Args:
        city: City name
        country: Country name
        minute_bucket: 5-minute time bucket for cache invalidation

    Returns:
        Tuple of (weather_dict, status_code)
    """
    try:
        location = Location(city=city, country=country)
        client = get_client()
        weather = client.get_weather(location)

        return (
            {
                "location": {
                    "city": weather.location.city,
                    "country": weather.location.country,
                    "latitude": weather.location.latitude,
                    "longitude": weather.location.longitude,
                },
                "temperature": weather.temperature,
                "condition": weather.condition,
                "humidity": weather.humidity,
                "wind_speed": weather.wind_speed,
            },
            200,
        )
    except Exception as e:
        return (
            {"error": "Failed to fetch weather data", "message": str(e)},
            500,
        )


@app.errorhandler(429)
def ratelimit_handler(e):  # type: ignore[no-untyped-def]
    """Handle rate limit exceeded errors."""
    logger.warning(
        "rate_limit_exceeded",
        ip=get_remote_address(),
        path=request.path,
        request_id=getattr(request, "id", None),
    )
    return (
        jsonify(
            {
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": str(e.description),
            }
        ),
        429,
    )


@app.before_request
def add_request_id() -> None:
    """Add unique request ID to each request."""
    request.id = str(uuid.uuid4())  # type: ignore[attr-defined]
    logger.info(
        "request_started",
        request_id=request.id,  # type: ignore[attr-defined]
        method=request.method,
        path=request.path,
        ip=get_remote_address(),
    )


@app.after_request
def add_request_id_header(response):  # type: ignore[no-untyped-def]
    """Add X-Request-ID header to response and log completion."""
    if hasattr(request, "id"):
        response.headers["X-Request-ID"] = request.id  # type: ignore[attr-defined]
        logger.info(
            "request_completed",
            request_id=request.id,  # type: ignore[attr-defined]
            status_code=response.status_code,
            path=request.path,
        )
    return response


@app.route("/api/health", methods=["GET"])
@app.route("/api/v1/health", methods=["GET"])
def health_check() -> tuple[dict[str, str], int]:
    """Health check endpoint (basic).

    Returns:
        JSON response with status
    """
    return jsonify({"status": "ok", "service": "MSN Weather Wrapper API", "version": "1.0"}), 200


@app.route("/api/v1/health/live", methods=["GET"])
def liveness_check() -> tuple[dict[str, str], int]:
    """Liveness probe endpoint.

    Returns:
        JSON response indicating the service is alive
    """
    return jsonify({"status": "alive", "service": "MSN Weather Wrapper API"}), 200


@app.route("/api/v1/health/ready", methods=["GET"])
def readiness_check() -> tuple[dict[str, str | bool], int]:
    """Readiness probe endpoint.

    Checks if the service and its dependencies are ready to serve requests.

    Returns:
        JSON response with readiness status and dependency checks
    """
    checks: dict[str, bool] = {}
    overall_ready = True

    # Check if weather client can be initialized
    try:
        client = get_client()
        checks["weather_client"] = True
    except Exception:
        checks["weather_client"] = False
        overall_ready = False

    # Check if we can make HTTP requests (test connection)
    try:
        # Quick HEAD request to MSN Weather
        response = client.session.head("https://www.msn.com", timeout=2)
        checks["external_api"] = response.status_code < 500
        if not checks["external_api"]:
            overall_ready = False
    except Exception:
        checks["external_api"] = False
        overall_ready = False

    status_code = 200 if overall_ready else 503
    return (
        jsonify(
            {
                "status": "ready" if overall_ready else "not_ready",
                "service": "MSN Weather Wrapper API",
                "checks": checks,
            }
        ),
        status_code,
    )


@app.route("/api/weather", methods=["GET"])
@app.route("/api/v1/weather", methods=["GET"])
@limiter.limit("30 per minute")
def get_weather() -> tuple[dict[str, str | float | int | dict[str, str]], int]:
    """Get weather data for a location.

    Query Parameters:
        city (str): City name (required)
        country (str): Country name (required)

    Returns:
        JSON response with weather data or error message

    Example:
        GET /api/weather?city=Seattle&country=USA
    """
    # Get query parameters
    city = request.args.get("city")
    country = request.args.get("country")

    # Validate required parameters
    if not city or not country:
        logger.warning(
            "missing_parameters",
            request_id=getattr(request, "id", None),
            city=city,
            country=country,
        )
        return (
            jsonify(
                {
                    "error": "Missing required parameters",
                    "message": "Both 'city' and 'country' parameters are required",
                }
            ),
            400,
        )

    # Validate and sanitize inputs
    city, city_error = validate_input(city, "city", MAX_CITY_LENGTH)
    if city_error:
        logger.warning(
            "invalid_city",
            request_id=getattr(request, "id", None),
            error=city_error,
        )
        return jsonify({"error": "Invalid input", "message": city_error}), 400

    country, country_error = validate_input(country, "country", MAX_COUNTRY_LENGTH)
    if country_error:
        logger.warning(
            "invalid_country",
            request_id=getattr(request, "id", None),
            error=country_error,
        )
        return jsonify({"error": "Invalid input", "message": country_error}), 400

    logger.info(
        "fetching_weather",
        request_id=getattr(request, "id", None),
        city=city,
        country=country,
    )

    # Use 5-minute cache buckets (0, 5, 10, 15, etc.)
    minute_bucket = datetime.now().minute // 5
    weather_data, status_code = get_cached_weather(city, country, minute_bucket)

    if status_code == 200:
        logger.info(
            "weather_fetched_successfully",
            request_id=getattr(request, "id", None),
            city=city,
            country=country,
            cached=True,
        )
        # Store in recent searches
        _add_to_recent_searches(city, country)
    else:
        logger.error(
            "weather_fetch_failed",
            request_id=getattr(request, "id", None),
            city=city,
            country=country,
            status_code=status_code,
        )

    return jsonify(weather_data), status_code


@app.route("/api/weather", methods=["POST"])
@app.route("/api/v1/weather", methods=["POST"])
@limiter.limit("30 per minute")
def get_weather_post() -> tuple[dict[str, str | float | int | dict[str, str]], int]:
    """Get weather data for a location (POST method).

    Request Body (JSON):
        {
            "city": "Seattle",
            "country": "USA"
        }

    Returns:
        JSON response with weather data or error message
    """
    # Get JSON data from request body
    try:
        data = request.get_json()
    except Exception as e:
        logger.warning(
            "invalid_json",
            request_id=getattr(request, "id", None),
            error=str(e),
        )
        return (
            jsonify({"error": "Invalid request", "message": "Request body must be valid JSON"}),
            400,
        )

    if not data or not isinstance(data, dict):
        logger.warning(
            "invalid_request_body",
            request_id=getattr(request, "id", None),
            data_type=type(data).__name__,
        )
        return (
            jsonify({"error": "Invalid request", "message": "Request body must be a JSON object"}),
            400,
        )

    city = data.get("city")
    country = data.get("country")

    # Validate required fields
    if not city or not country:
        logger.warning(
            "missing_fields",
            request_id=getattr(request, "id", None),
            city=city,
            country=country,
        )
        return (
            jsonify(
                {
                    "error": "Missing required fields",
                    "message": "Both 'city' and 'country' fields are required",
                }
            ),
            400,
        )

    # Validate and sanitize inputs
    city, city_error = validate_input(city, "city", MAX_CITY_LENGTH)
    if city_error:
        logger.warning(
            "invalid_city_post",
            request_id=getattr(request, "id", None),
            error=city_error,
        )
        return jsonify({"error": "Invalid input", "message": city_error}), 400

    country, country_error = validate_input(country, "country", MAX_COUNTRY_LENGTH)
    if country_error:
        logger.warning(
            "invalid_country_post",
            request_id=getattr(request, "id", None),
            error=country_error,
        )
        return jsonify({"error": "Invalid input", "message": country_error}), 400

    logger.info(
        "fetching_weather_post",
        request_id=getattr(request, "id", None),
        city=city,
        country=country,
    )

    # Use 5-minute cache buckets (0, 5, 10, 15, etc.)
    minute_bucket = datetime.now().minute // 5
    weather_data, status_code = get_cached_weather(city, country, minute_bucket)

    if status_code == 200:
        logger.info(
            "weather_fetched_successfully_post",
            request_id=getattr(request, "id", None),
            city=city,
            country=country,
            cached=True,
        )
        # Store in recent searches
        _add_to_recent_searches(city, country)
    else:
        logger.error(
            "weather_fetch_failed_post",
            request_id=getattr(request, "id", None),
            city=city,
            country=country,
            status_code=status_code,
        )

    return jsonify(weather_data), status_code


def _add_to_recent_searches(city: str, country: str) -> None:
    """Add a search to recent searches history.

    Args:
        city: City name
        country: Country name
    """
    session_id = session.get("id")
    if not session_id:
        session_id = str(uuid.uuid4())
        session["id"] = session_id

    if session_id not in recent_searches:
        recent_searches[session_id] = deque(maxlen=10)

    search_entry = {"city": city, "country": country}

    # Remove duplicates and add to front
    searches = recent_searches[session_id]
    if search_entry in searches:
        searches.remove(search_entry)
    searches.appendleft(search_entry)


@app.route("/api/v1/weather/coordinates", methods=["GET"])
@limiter.limit("30 per minute")
def get_weather_by_coordinates() -> tuple[dict[str, Any], int]:
    """Get weather data by latitude and longitude.

    Query Parameters:
        lat (float): Latitude (required)
        lon (float): Longitude (required)

    Returns:
        JSON response with weather data or error message

    Example:
        GET /api/v1/weather/coordinates?lat=47.6062&lon=-122.3321
    """
    lat_str = request.args.get("lat")
    lon_str = request.args.get("lon")

    # Validate required parameters
    if not lat_str or not lon_str:
        logger.warning(
            "missing_coordinates",
            request_id=getattr(request, "id", None),
            lat=lat_str,
            lon=lon_str,
        )
        return (
            jsonify(
                {
                    "error": "Missing required parameters",
                    "message": "Both 'lat' and 'lon' parameters are required",
                }
            ),
            400,
        )

    # Validate coordinate format
    try:
        lat = float(lat_str)
        lon = float(lon_str)

        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")
    except ValueError as e:
        logger.warning(
            "invalid_coordinates",
            request_id=getattr(request, "id", None),
            lat=lat_str,
            lon=lon_str,
            error=str(e),
        )
        return jsonify({"error": "Invalid coordinates", "message": str(e)}), 400

    logger.info(
        "fetching_weather_by_coordinates",
        request_id=getattr(request, "id", None),
        lat=lat,
        lon=lon,
    )

    try:
        client = get_client()
        weather = client.get_weather_by_coordinates(lat, lon)

        weather_data = {
            "location": {
                "city": weather.location.city,
                "country": weather.location.country,
                "latitude": weather.location.latitude,
                "longitude": weather.location.longitude,
            },
            "temperature": weather.temperature,
            "condition": weather.condition,
            "humidity": weather.humidity,
            "wind_speed": weather.wind_speed,
        }

        logger.info(
            "weather_fetched_by_coordinates_successfully",
            request_id=getattr(request, "id", None),
            lat=lat,
            lon=lon,
            city=weather.location.city,
        )

        return jsonify(weather_data), 200

    except Exception as e:
        logger.error(
            "weather_fetch_by_coordinates_failed",
            request_id=getattr(request, "id", None),
            lat=lat,
            lon=lon,
            error=str(e),
        )
        return (
            jsonify({"error": "Failed to fetch weather data", "message": str(e)}),
            500,
        )


@app.route("/api/v1/recent-searches", methods=["GET"])
def get_recent_searches() -> tuple[dict[str, list[dict[str, str]]], int]:
    """Get recent weather searches for the current session.

    Returns:
        JSON response with list of recent searches
    """
    session_id = session.get("id")
    if not session_id or session_id not in recent_searches:
        return jsonify({"recent_searches": []}), 200

    searches = list(recent_searches[session_id])
    return jsonify({"recent_searches": searches}), 200


@app.route("/api/v1/recent-searches", methods=["DELETE"])
def clear_recent_searches() -> tuple[dict[str, str], int]:
    """Clear recent weather searches for the current session.

    Returns:
        JSON response confirming deletion
    """
    session_id = session.get("id")
    if session_id and session_id in recent_searches:
        del recent_searches[session_id]

    return jsonify({"message": "Recent searches cleared"}), 200


@app.teardown_appcontext
def cleanup(error: Exception | None = None) -> None:
    """Clean up resources on app shutdown."""
    if hasattr(app, "weather_client"):
        app.weather_client.close()


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
