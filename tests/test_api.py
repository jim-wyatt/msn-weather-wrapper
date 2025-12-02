"""Tests for the Flask API."""

import json
from unittest.mock import MagicMock, patch

import pytest

from api import app
from msn_weather_wrapper.models import Location, WeatherData


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "ok"
    assert "service" in data


def test_get_weather_missing_parameters(client):
    """Test GET weather endpoint with missing parameters."""
    response = client.get("/api/weather")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_get_weather_missing_city(client):
    """Test GET weather endpoint with missing city."""
    response = client.get("/api/weather?country=USA")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


@patch("api.get_client")
def test_get_weather_success(mock_get_client, client):
    """Test GET weather endpoint with valid parameters."""
    # Setup mock
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    mock_weather = WeatherData(
        location=Location(city="Seattle", country="USA"),
        temperature=15.5,
        condition="Partly Cloudy",
        humidity=65,
        wind_speed=12.5,
    )
    mock_client.get_weather.return_value = mock_weather

    response = client.get("/api/weather?city=Seattle&country=USA")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "location" in data
    assert "temperature" in data
    assert "condition" in data
    assert "humidity" in data
    assert "wind_speed" in data
    assert data["location"]["city"] == "Seattle"
    assert data["location"]["country"] == "USA"


def test_post_weather_missing_body(client):
    """Test POST weather endpoint with missing body."""
    response = client.post("/api/weather", data=json.dumps({}), content_type="application/json")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_post_weather_missing_fields(client):
    """Test POST weather endpoint with missing fields."""
    response = client.post(
        "/api/weather", data=json.dumps({"city": "Seattle"}), content_type="application/json"
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


@patch("api.get_client")
def test_post_weather_success(mock_get_client, client):
    """Test POST weather endpoint with valid data."""
    # Setup mock
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    mock_weather = WeatherData(
        location=Location(city="London", country="UK"),
        temperature=10.2,
        condition="Rainy",
        humidity=85,
        wind_speed=20.0,
    )
    mock_client.get_weather.return_value = mock_weather

    response = client.post(
        "/api/weather",
        data=json.dumps({"city": "London", "country": "UK"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "location" in data
    assert "temperature" in data
    assert "condition" in data
    assert "humidity" in data
    assert "wind_speed" in data
    assert data["location"]["city"] == "London"
    assert data["location"]["country"] == "UK"
    assert isinstance(data["temperature"], (int, float))
    assert 0 <= data["humidity"] <= 100
    assert data["wind_speed"] >= 0


@patch("api.get_client")
def test_get_weather_client_error(mock_get_client, client):
    """Test GET weather endpoint when client raises an error."""
    # Clear the cache to ensure mock is used
    from api import get_cached_weather

    get_cached_weather.cache_clear()

    # Setup mock to raise exception
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.get_weather.side_effect = Exception("Network error")

    response = client.get("/api/weather?city=Seattle&country=USA")
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "message" in data


@patch("api.get_client")
def test_post_weather_client_error(mock_get_client, client):
    """Test POST weather endpoint when client raises an error."""
    # Clear the cache to ensure mock is used
    from api import get_cached_weather

    get_cached_weather.cache_clear()

    # Setup mock to raise exception
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.get_weather.side_effect = ValueError("Invalid data")

    response = client.post(
        "/api/weather",
        data=json.dumps({"city": "Invalid", "country": "XX"}),
        content_type="application/json",
    )
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "message" in data


def test_post_weather_invalid_json(client):
    """Test POST weather endpoint with invalid JSON."""
    response = client.post(
        "/api/weather",
        data="not valid json",
        content_type="application/json",
    )
    assert response.status_code == 400


def test_invalid_endpoint(client):
    """Test invalid API endpoint."""
    response = client.get("/api/invalid")
    assert response.status_code == 404
