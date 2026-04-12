"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error payload."""

    error: str
    message: str


class LocationResponse(BaseModel):
    """Serialized location information."""

    city: str
    country: str
    latitude: float | None = None
    longitude: float | None = None


class WeatherResponse(BaseModel):
    """Serialized weather data."""

    location: LocationResponse
    temperature: float | int
    condition: str
    humidity: int
    wind_speed: float | int


class HealthResponse(BaseModel):
    """Health endpoint response."""

    status: str
    service: str
    version: str | None = None
    checks: dict[str, bool] | None = None


class RecentSearchItem(BaseModel):
    """Recent search entry."""

    city: str
    country: str


class RecentSearchesResponse(BaseModel):
    """Recent searches collection."""

    recent_searches: list[RecentSearchItem]


class MessageResponse(BaseModel):
    """Simple message payload."""

    message: str
