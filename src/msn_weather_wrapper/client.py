"""Weather client for interacting with MSN Weather services."""

import json
import re
from typing import TypeVar
from urllib.parse import quote

import httpx  # type: ignore[import-not-found]
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim  # type: ignore[import-not-found, import-untyped]
from tenacity import retry, stop_after_attempt, wait_exponential  # type: ignore[import-not-found]

from msn_weather_wrapper.exceptions import (
    LocationNotFoundError,
    ParsingError,
    UpstreamError,
    WeatherError,
)
from msn_weather_wrapper.models import Location, WeatherData

T = TypeVar("T", bound="BaseWeatherClient")


class BaseWeatherClient:
    """Base class for weather clients with shared extraction logic."""

    def __init__(self, timeout: int = 10) -> None:
        """Initialize the base weather client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.base_url = "https://www.msn.com/en-us/weather/forecast/in-"
        self.geocoder = Nominatim(user_agent="msn-weather-wrapper")

    def _get_location_url(self, location: Location) -> str:
        """Construct the URL for the location."""
        location_str = f"{location.city},{location.country}"
        encoded_location = quote(location_str)
        return f"{self.base_url}{encoded_location}"

    def _parse_weather_response(self, html: str, location: Location) -> WeatherData:
        """Parse weather data from an HTML response.

        Args:
            html: The raw HTML content returned by the MSN Weather service.
            location: The location associated with the weather data being parsed.

        Returns:
            A :class:`WeatherData` instance containing the parsed temperature,
            condition, humidity, and wind speed for the given location.

        Raises:
            ParsingError: If the weather data cannot be parsed from the HTML
                content, for example when required values are missing or have
                an unexpected format.
        """
        # Try to extract weather data from embedded JSON
        weather_data = self._extract_weather_from_json(html)
        if weather_data:
            return WeatherData(
                location=location,
                temperature=float(weather_data["temperature"]),
                condition=str(weather_data["condition"]),
                humidity=int(weather_data["humidity"]),
                wind_speed=float(weather_data["wind_speed"]),
            )

        # Fallback to HTML parsing if JSON extraction fails
        soup = BeautifulSoup(html, "lxml")
        try:
            temperature = self._extract_temperature(soup)
            condition = self._extract_condition(soup)
            humidity = self._extract_humidity(soup)
            wind_speed = self._extract_wind_speed(soup)

            return WeatherData(
                location=location,
                temperature=temperature,
                condition=condition,
                humidity=humidity,
                wind_speed=wind_speed,
            )
        except ValueError as e:
            raise ParsingError(f"Failed to parse weather data: {str(e)}") from e

    def _extract_weather_from_json(self, html: str) -> dict[str, float | int | str] | None:
        """Extract weather data from embedded JSON in the HTML.

        Args:
            html: The HTML content

        Returns:
            Dictionary with temperature, condition, humidity, and wind_speed, or None if not found
        """
        try:
            # Parse script tags with type="application/json"
            soup = BeautifulSoup(html, "lxml")

            for script in soup.find_all("script", type="application/json"):
                try:
                    data = json.loads(script.string)

                    # Navigate to WeatherData._@STATE@_.forecast[0].hourly
                    if "WeatherData" not in data:
                        continue

                    weather_data = data["WeatherData"]
                    if "_@STATE@_" not in weather_data:
                        continue

                    state = weather_data["_@STATE@_"]
                    if "forecast" not in state or not isinstance(state["forecast"], list):
                        continue

                    if len(state["forecast"]) == 0:
                        continue

                    forecast = state["forecast"][0]
                    if "hourly" not in forecast or not isinstance(forecast["hourly"], list):
                        continue

                    if len(forecast["hourly"]) == 0:
                        continue

                    # Get the first hourly entry (current conditions)
                    current = forecast["hourly"][0]

                    # Extract weather information
                    temp_f = float(current.get("temperature", 0))
                    # Convert Fahrenheit to Celsius
                    temp_c = round((temp_f - 32) * 5 / 9, 1)

                    # Get condition from cap or symbol
                    condition = current.get("cap", current.get("summary", "Unknown"))

                    # Get humidity (remove % sign if present)
                    humidity_str = str(current.get("humidity", "50"))
                    humidity = int(humidity_str.rstrip("%"))

                    # Get wind speed (in mph, convert to km/h)
                    wind_speed_str = str(current.get("windSpeed", "0"))
                    wind_mph = float(wind_speed_str)
                    wind_kmh = round(wind_mph * 1.60934, 1)

                    return {
                        "temperature": temp_c,
                        "condition": condition,
                        "humidity": humidity,
                        "wind_speed": wind_kmh,
                    }

                except (json.JSONDecodeError, KeyError, ValueError, AttributeError, TypeError):
                    continue

            return None

        except Exception:
            return None

    def _extract_temperature(self, soup: BeautifulSoup) -> float:
        """Extract temperature from the page."""
        # Try to find temperature in common locations
        temp_selectors = [
            'span[class*="temp"]',
            'div[class*="temp"]',
            '[data-testid*="temperature"]',
            'span[class*="CurrentConditions"]',
        ]

        for selector in temp_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                # Look for temperature patterns like "72°", "72", "72°F", "22°C"
                match = re.search(r"(-?\d+\.?\d*)", text)
                if match:
                    temp = float(match.group(1))
                    # Convert Fahrenheit to Celsius if needed
                    if "°F" in text or "F" in text:
                        temp = (temp - 32) * 5 / 9
                    return round(temp, 1)

        raise ValueError("Could not extract temperature from page")

    def _extract_condition(self, soup: BeautifulSoup) -> str:
        """Extract weather condition from the page."""
        # Try to find condition in common locations
        condition_selectors = [
            '[class*="condition"]',
            '[class*="weather"]',
            '[data-testid*="condition"]',
            'div[class*="caption"]',
        ]

        for selector in condition_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                # Filter out numbers and very short strings
                if text and len(text) > 2 and not text.isdigit():
                    return str(text)

        # Fallback to searching for common weather terms
        weather_terms = [
            "Sunny",
            "Cloudy",
            "Partly Cloudy",
            "Rainy",
            "Clear",
            "Overcast",
            "Thunderstorm",
        ]
        page_text = soup.get_text()
        for term in weather_terms:
            if term in page_text:
                return term

        return "Unknown"

    def _extract_humidity(self, soup: BeautifulSoup) -> int:
        """Extract humidity from the page."""
        # Search for humidity in the page text
        page_text = soup.get_text()
        # Look for patterns like "Humidity: 65%" or "65% humidity"
        match = re.search(r"humidity[:\s]*(\d+)%|(\d+)%\s*humidity", page_text, re.IGNORECASE)
        if match:
            humidity_str = match.group(1) or match.group(2)
            return int(humidity_str)

        # Try finding elements with humidity in class or attribute
        humidity_elements = soup.find_all(string=re.compile(r"\d+%"))
        for element in humidity_elements:
            if "humid" in str(element.parent).lower():
                match = re.search(r"(\d+)%", element)
                if match:
                    return int(match.group(1))

        # Default value if not found
        return 50

    def _extract_wind_speed(self, soup: BeautifulSoup) -> float:
        """Extract wind speed from the page."""
        # Search for wind speed in the page text
        page_text = soup.get_text()
        # Look for patterns like "Wind: 10 mph" or "10 km/h wind"
        match = re.search(
            r"wind[:\s]*(\d+\.?\d*)\s*(mph|km/h|m/s)|(\d+\.?\d*)\s*(mph|km/h|m/s)\s*wind",
            page_text,
            re.IGNORECASE,
        )
        if match:
            speed_str = match.group(1) or match.group(3)
            unit = match.group(2) or match.group(4)
            speed = float(speed_str)

            # Convert to km/h
            if unit.lower() == "mph":
                speed = speed * 1.60934
            elif unit.lower() == "m/s":
                speed = speed * 3.6

            return round(speed, 1)

        # Default value if not found
        return 0.0

    def _reverse_geocode_to_location(self, latitude: float, longitude: float) -> Location:
        """Reverse geocode coordinates to a Location object.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Location object with city, country, and coordinates

        Raises:
            LocationNotFoundError: If location cannot be determined
            WeatherError: If reverse geocoding fails
        """
        try:
            location_data = self.geocoder.reverse(f"{latitude}, {longitude}", language="en")  # type: ignore[call-arg, misc]
            if not location_data:
                raise LocationNotFoundError(
                    f"Could not determine location for coordinates {latitude}, {longitude}"
                )

            address = location_data.raw.get("address", {})  # type: ignore[union-attr]
            city = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("county")
                or "Unknown"
            )
            country = address.get("country", "Unknown")

            return Location(city=city, country=country, latitude=latitude, longitude=longitude)

        except LocationNotFoundError:
            raise
        except Exception as e:
            raise WeatherError(f"Failed to reverse geocode coordinates: {str(e)}") from e


class WeatherClient(BaseWeatherClient):
    """Synchronous client for fetching weather data from MSN Weather."""

    def __init__(self, timeout: int = 10) -> None:
        """Initialize the weather client.

        Args:
            timeout: Request timeout in seconds
        """
        super().__init__(timeout)
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )

    @retry(  # type: ignore[misc]
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=lambda e: isinstance(e, requests.RequestException),
    )
    def get_weather(self, location: Location) -> WeatherData:
        """Get current weather data for a location.

        Args:
            location: Location to get weather for

        Returns:
            Weather data for the specified location

        Raises:
            UpstreamError: If the request fails
            ParsingError: If weather data cannot be parsed from the page
        """
        url = self._get_location_url(location)

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            raise UpstreamError(f"Failed to fetch weather data from MSN: {str(e)}") from e

        return self._parse_weather_response(response.text, location)

    def get_weather_by_coordinates(self, latitude: float, longitude: float) -> WeatherData:
        """Get current weather data for a location by coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Weather data for the specified coordinates

        Raises:
            LocationNotFoundError: If location cannot be determined
            WeatherError: If weather data cannot be fetched or parsed
        """
        location = self._reverse_geocode_to_location(latitude, longitude)
        return self.get_weather(location)

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "WeatherClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit."""
        self.close()


class AsyncWeatherClient(BaseWeatherClient):
    """Asynchronous client for fetching weather data from MSN Weather."""

    def __init__(self, timeout: int = 10) -> None:
        """Initialize the async weather client.

        Args:
            timeout: Request timeout in seconds
        """
        super().__init__(timeout)
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )

    @retry(  # type: ignore[misc]
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=lambda e: isinstance(e, httpx.HTTPError),
    )
    async def get_weather(self, location: Location) -> WeatherData:
        """Get current weather data for a location asynchronously.

        Args:
            location: Location to get weather for

        Returns:
            Weather data for the specified location

        Raises:
            UpstreamError: If the request fails
            ParsingError: If weather data cannot be parsed from the page
        """
        url = self._get_location_url(location)

        try:
            response = await self.client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise UpstreamError(f"Failed to fetch weather data from MSN: {str(e)}") from e

        return self._parse_weather_response(response.text, location)

    async def get_weather_by_coordinates(self, latitude: float, longitude: float) -> WeatherData:
        """Get current weather data for a location by coordinates asynchronously.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Weather data for the specified coordinates

        Raises:
            LocationNotFoundError: If location cannot be determined
            WeatherError: If weather data cannot be fetched or parsed
        """
        # Note: geopy is synchronous, but the shared helper handles this
        location = self._reverse_geocode_to_location(latitude, longitude)
        return await self.get_weather(location)
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "AsyncWeatherClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.close()
