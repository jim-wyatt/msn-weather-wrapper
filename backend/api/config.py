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
    """Return configured CORS origins; an empty setting disables cross-origin access."""
    raw_value = os.getenv("CORS_ORIGINS", "")
    origins = [origin.strip() for origin in raw_value.split(",") if origin.strip()]
    if "*" in origins:
        raise ValueError(
            "CORS_ORIGINS must list explicit origins; '*' is not allowed. "
            "Set it to a comma-separated list, e.g. https://app.example.com"
        )
    return origins


MIN_SECRET_KEY_LENGTH = 32


def _read_secret_key_file(path: str) -> str:
    """Read a secret from a file (Docker/Podman secrets, Kubernetes mounted secrets)."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read().strip()
    except OSError as error:
        raise ValueError(f"APP_SECRET_KEY_FILE could not be read: {error}") from error


def get_secret_key() -> str:
    """Resolve the app secret key with secure development fallback.

    Resolution order: ``APP_SECRET_KEY_FILE`` (a file containing the key, so the value
    never appears in the environment or ``docker inspect``), then ``APP_SECRET_KEY``.
    Outside development/testing the key must be set and at least 32 characters long.
    """
    secret_key: str | None = None
    secret_file = os.getenv("APP_SECRET_KEY_FILE")
    if secret_file:
        secret_key = _read_secret_key_file(secret_file)
    if not secret_key:
        secret_key = os.getenv("APP_SECRET_KEY")

    if secret_key and secret_key != DEFAULT_SECRET_KEY_PLACEHOLDER:
        if len(secret_key) < MIN_SECRET_KEY_LENGTH and not (
            ENVIRONMENT == "development" or DEBUG or TESTING
        ):
            raise ValueError(
                f"APP_SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} characters in "
                "production. Generate one with: "
                "python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        return secret_key

    if ENVIRONMENT == "development" or DEBUG or TESTING:
        return secrets.token_hex(32)

    raise ValueError(
        "APP_SECRET_KEY (or APP_SECRET_KEY_FILE) must be set in production. "
        "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
    )
