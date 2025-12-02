"""Data models for weather information."""

from typing import Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    """Geographic location."""

    city: str = Field(description="City name")
    country: str = Field(description="Country name")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")


class WeatherData(BaseModel):
    """Weather data for a location."""

    location: Location = Field(description="Location information")
    temperature: float = Field(description="Temperature in Celsius")
    condition: str = Field(description="Weather condition description")
    humidity: int = Field(ge=0, le=100, description="Humidity percentage")
    wind_speed: float = Field(ge=0, description="Wind speed in km/h")
