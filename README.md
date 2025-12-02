# MSN Weather Wrapper

> A modern, production-ready Python wrapper for MSN Weather with Flask REST API and React frontend.

[![PyPI version](https://img.shields.io/pypi/v/msn-weather-wrapper.svg)](https://pypi.org/project/msn-weather-wrapper/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-67%20passing-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-89%25-success)](tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jim-wyatt.github.io/msn-weather-wrapper/)

---

## Overview

MSN Weather Wrapper is a comprehensive weather data solution featuring:
- **Python Library** - Type-safe weather client with Pydantic models
- **REST API** - Production-ready Flask API with security & rate limiting
- **Web Frontend** - Modern React 19 + TypeScript 5.7+ with Vite 7
- **Containerized** - Podman/Docker deployment with Gunicorn & Nginx

---

## Quick Start

### 🚀 Containerized Deployment (Recommended)

Deploy the complete stack in seconds:

```bash
git clone https://github.com/jim-wyatt/msn-weather-wrapper.git
cd msn-weather-wrapper

# Start the application
podman-compose up -d

# Access at http://localhost:8080
```

### 🧪 Development Environment

Get a hot-reload development environment with all dependencies:

```bash
# One-command setup
./bootstrap-dev.sh setup

# Start development servers
./bootstrap-dev.sh start

# Access:
# - Frontend: http://localhost:5173
# - API: http://localhost:5000
```

### 📦 Python Package

Install and use in your Python projects:

```bash
pip install msn-weather-wrapper
```

```python
from msn_weather_wrapper import WeatherClient, Location

with WeatherClient() as client:
    location = Location(city="London", country="UK")
    weather = client.get_weather(location)
    
    print(f"Temperature: {weather.temperature}°C")
    print(f"Condition: {weather.condition}")
```

---

## Features

### Core Capabilities
- 🌤️ Weather data extraction from MSN Weather
- 🌍 406+ cities worldwide with autocomplete
- �� RESTful API with comprehensive validation
- ⚛️ Modern web interface with React + TypeScript
- 🚀 5-minute caching (90%+ faster repeated requests)
- 🔒 Rate limiting (30 req/min per IP, 200/hr global)

### Security & Quality
- 🛡️ Input validation & attack prevention (SQL injection, XSS, etc.)
- ✅ 77 tests with 89% coverage
- 🔍 Type safety with mypy strict mode
- 🎨 Code quality with ruff linting
- 📋 SBOM generation for supply chain security
- 🔐 Zero known vulnerabilities

### Technology Stack
- **Backend**: Python 3.9+, Flask 3.1+, Pydantic 2.12+, Gunicorn 23.0+
- **Frontend**: React 19.2, Vite 7.2, TypeScript 5.7+
- **Testing**: pytest 9.0+, Playwright, 77 tests
- **Quality**: ruff 0.14+, mypy 1.19+, pre-commit hooks
- **Deployment**: Podman/Docker, Nginx, multi-stage builds

---

## Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 20+ (for frontend development)
- Podman or Docker (for containerized deployment)

### Option 1: From PyPI

```bash
pip install msn-weather-wrapper
```

### Option 2: From Source

```bash
git clone https://github.com/jim-wyatt/msn-weather-wrapper.git
cd msn-weather-wrapper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

---

## Usage

### Python Library

```python
from msn_weather_wrapper import WeatherClient, Location

# Create client
with WeatherClient() as client:
    # Get weather for a city
    location = Location(city="Seattle", country="USA")
    weather = client.get_weather(location)
    
    # Access weather data
    print(f"Temperature: {weather.temperature}°C")
    print(f"Feels Like: {weather.feels_like}°C")
    print(f"Condition: {weather.condition}")
    print(f"Humidity: {weather.humidity}%")
    print(f"Wind Speed: {weather.wind_speed} km/h")
```

### REST API

**Start the server:**
```bash
# Development
python api.py

# Production (with Gunicorn)
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 api:app
```

**Make requests:**
```bash
# GET request
curl "http://localhost:5000/api/weather?city=London&country=UK"

# POST request
curl -X POST http://localhost:5000/api/weather \
  -H "Content-Type: application/json" \
  -d '{"city": "London", "country": "UK"}'
```

**Response:**
```json
{
  "temperature": 15.5,
  "feels_like": 14.2,
  "condition": "Partly Cloudy",
  "humidity": 72,
  "wind_speed": 15.2,
  "location": "London, UK"
}
```

### Web Frontend

**Local development:**
```bash
cd frontend
npm install
npm run dev  # Starts at http://localhost:5173
```

**Features:**
- 🔍 City autocomplete with 406+ cities
- 🌡️ Temperature unit toggle (°C/°F)
- 📍 Geolocation support
- 📱 Responsive mobile-friendly design
- ♿ WCAG 2.1 Level AA accessibility

---

## Documentation

📚 **[Full Documentation](https://jim-wyatt.github.io/msn-weather-wrapper/)**

| Document | Description |
|----------|-------------|
| [API Reference](docs/API.md) | Complete REST API documentation |
| [Development Guide](docs/DEVELOPMENT.md) | Setup & development workflow |
| [Container Dev Setup](docs/CONTAINER_DEV_SETUP.md) | Containerized development |
| [Testing Guide](docs/TESTING.md) | Test suite & coverage |
| [Security Guide](docs/SECURITY.md) | Security features & testing |
| [SBOM Guide](docs/SYFT_GUIDE.md) | Software bill of materials |
| [Changelog](docs/CHANGELOG.md) | Version history |

---

## Development

### Development Setup

```bash
# Containerized (Recommended)
./bootstrap-dev.sh setup   # One-time setup
./bootstrap-dev.sh start   # Start dev environment
./bootstrap-dev.sh test    # Run all tests
./bootstrap-dev.sh logs    # View logs

# Local Development
pip install -e ".[dev]"    # Install dependencies
pre-commit install         # Setup git hooks
pytest                     # Run tests
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy src/msn_weather_wrapper

# Run all checks
pre-commit run --all-files
```

### Testing

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_client.py -v

# Integration tests (requires running containers)
podman-compose up -d
pytest tests/test_integration.py -v
```

---

## Deployment

### Podman Compose (Recommended)

```bash
# Build and start
podman-compose up -d

# View logs
podman-compose logs -f

# Stop
podman-compose down
```

### Standalone Container

```bash
# Build
podman build -t msn-weather-wrapper .

# Run
podman run -p 8080:80 msn-weather-wrapper
```

### Architecture
- **Unified Container**: Python + Node.js multi-stage build
- **Web Server**: Nginx (reverse proxy + static files)
- **API Server**: Gunicorn WSGI (4 workers, 120s timeout)
- **Process Manager**: Supervisor (manages nginx + gunicorn)
- **Health Checks**: Kubernetes-ready probes

---

## Contributing

Contributions are welcome! Please ensure:

1. ✅ All tests pass: `pytest`
2. 🎨 Code is formatted: `ruff format .`
3. 🔍 Type checks pass: `mypy src/`
4. 🪝 Pre-commit hooks pass
5. 📝 Documentation is updated

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## Project Structure

```
msn-weather-wrapper/
├── src/msn_weather_wrapper/    # Python package
│   ├── client.py               # Weather client
│   ├── models.py               # Pydantic models
│   └── __init__.py
├── tests/                      # Test suite (77 tests)
├── frontend/                   # React application
│   ├── src/                    # TypeScript source
│   └── tests/                  # E2E tests
├── api.py                      # Flask REST API
├── docs/                       # Documentation
├── Containerfile               # Production container
├── podman-compose.yml          # Orchestration
└── pyproject.toml              # Python config
```

---

## Security

### Security Features
- ✅ Input validation & sanitization
- ✅ SQL injection protection
- ✅ XSS prevention
- ✅ Path traversal protection
- ✅ Command injection prevention
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ 25 dedicated security tests

See [SECURITY.md](docs/SECURITY.md) for details.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Links

- 📖 [Documentation](https://jim-wyatt.github.io/msn-weather-wrapper/)
- 📦 [PyPI Package](https://pypi.org/project/msn-weather-wrapper/)
- 🐛 [Issue Tracker](https://github.com/jim-wyatt/msn-weather-wrapper/issues)
- 💬 [Discussions](https://github.com/jim-wyatt/msn-weather-wrapper/discussions)

---

## Disclaimer

This project is an unofficial wrapper for MSN Weather data and is provided for educational and personal use only. This software is not affiliated with, endorsed by, or officially connected to Microsoft Corporation or MSN Weather in any way.

For production weather data needs, please use official weather APIs with proper licensing.

---

<div align="center">

**Built with ❤️ using Python, Flask, and React**

[Get Started](#quick-start) · [Documentation](https://jim-wyatt.github.io/msn-weather-wrapper/) · [GitHub](https://github.com/jim-wyatt/msn-weather-wrapper)

</div>
