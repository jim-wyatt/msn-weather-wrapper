"""MSN Weather Wrapper - A Python wrapper for MSN Weather services."""

__version__ = "0.1.0"

from msn_weather_wrapper.client import WeatherClient
from msn_weather_wrapper.models import Location, WeatherData

__all__ = ["WeatherClient", "WeatherData", "Location"]
