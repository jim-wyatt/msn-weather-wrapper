"""Configuration helpers for the FastAPI service."""

from __future__ import annotations

import os
import secrets

from dotenv import load_dotenv

DEFAULT_SECRET_KEY_PLACEHOLDER = "change-this-to-a-secure-random-key-in-production"  # nosec B105

if os.path.exists("/app/.env.production"):
    load_dotenv("/app/.env.production")
else:
    load_dotenv()


ENVIRONMENT = os.getenv("APP_ENV", "production")
DEBUG = os.getenv("APP_DEBUG", "0") == "1"
TESTING = os.getenv("TESTING", "0") == "1"
HOST = os.getenv("HOST", "0.0.0.0")  # nosec B104
PORT = int(os.getenv("PORT", "5000"))

RATE_LIMIT_PER_IP = os.getenv("RATE_LIMIT_PER_IP", "30")
RATE_LIMIT_GLOBAL = os.getenv("RATE_LIMIT_GLOBAL", "200")

MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "100"))
MAX_CITY_LENGTH = MAX_INPUT_LENGTH
MAX_COUNTRY_LENGTH = MAX_INPUT_LENGTH

CACHE_SIZE = int(os.getenv("CACHE_SIZE", "1000"))
# CACHE_DURATION env var is expressed in seconds; convert to minutes for bucket arithmetic.
CACHE_DURATION_MINUTES = int(os.getenv("CACHE_DURATION", "300")) // 60


def get_cors_origins() -> list[str]:
    """Return configured CORS origins as a normalized list."""
    raw_value = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    if raw_value.strip() == "*":
        return ["*"]
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


def get_secret_key() -> str:
    """Resolve the app secret key with secure development fallback."""
    secret_key = os.getenv("APP_SECRET_KEY")

    if secret_key and secret_key != DEFAULT_SECRET_KEY_PLACEHOLDER:
        return secret_key

    if ENVIRONMENT == "development" or DEBUG or TESTING:
        return secrets.token_hex(32)

    raise ValueError(
        "APP_SECRET_KEY must be set in production. "
        "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
    )
