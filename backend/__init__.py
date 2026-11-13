"""MSN Weather Wrapper: Python client and FastAPI service for MSN Weather data."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

from backend.client import WeatherClient
from backend.models import Location, WeatherData

try:
    # The version is derived from the git tag at build time (hatch-vcs); the
    # container image passes it in as a build argument.
    __version__ = _distribution_version("msn-weather-wrapper")
except PackageNotFoundError:  # a checkout without an installed distribution
    __version__ = "0.0.0+unknown"

__all__ = ["WeatherClient", "WeatherData", "Location", "__version__"]
