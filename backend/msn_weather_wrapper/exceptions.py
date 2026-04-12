"""Custom exceptions for MSN Weather Wrapper."""


class WeatherError(Exception):
    """Base exception for all weather-related errors."""


class UpstreamError(WeatherError):
    """Raised when the upstream MSN Weather service returns an error."""


class ParsingError(WeatherError):
    """Raised when weather data cannot be parsed from the response."""


class LocationNotFoundError(WeatherError):
    """Raised when a location cannot be found or geocoded."""
