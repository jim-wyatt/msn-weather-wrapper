"""MSN Weather Wrapper - A Python wrapper for MSN Weather services."""

__version__ = "2.0.4"

from backend.client import WeatherClient
from backend.models import Location, WeatherData

__all__ = ["WeatherClient", "WeatherData", "Location"]
