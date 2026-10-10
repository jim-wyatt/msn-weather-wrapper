# MSN Weather Wrapper

> A modern, production-ready Python wrapper for MSN Weather with a FastAPI backend and Next.js frontend.

[![CI/CD Pipeline](https://github.com/jim-wyatt/msn-weather-wrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/jim-wyatt/msn-weather-wrapper/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/msn-weather-wrapper.svg)](https://pypi.org/project/msn-weather-wrapper/)
[![Python](https://img.shields.io/pypi/pyversions/msn-weather-wrapper.svg)](https://pypi.org/project/msn-weather-wrapper/)
[![License](https://img.shields.io/github/license/jim-wyatt/msn-weather-wrapper.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jim-wyatt.github.io/msn-weather-wrapper/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![Container](https://img.shields.io/badge/container-ghcr.io-blue)](https://github.com/jim-wyatt/msn-weather-wrapper/pkgs/container/msn-weather-wrapper)

---

## Overview

MSN Weather Wrapper is a comprehensive weather data solution featuring:

- **Python Library** - Type-safe weather client with Pydantic models
- **REST API** - Production-ready FastAPI service with built-in OpenAPI docs
- **Web Frontend** - Modern Next.js 16 + React 19 + TypeScript
- **Containerized** - Podman/Docker deployment with Gunicorn, Uvicorn workers, and Nginx

**Technology Stack:**

- **Backend**: Python 3.10+, FastAPI 0.115+, Pydantic 2.12+, Uvicorn, Gunicorn 23.0+
- **Frontend**: Next.js 16, React 19, TypeScript
- **Testing**: pytest and Playwright (unit, security, integration, accessibility, and end-to-end suites)
- **Quality**: ruff, mypy (strict), pre-commit hooks
- **Security**: Bandit, Semgrep, pip-audit, Trivy, Grype, weekly automated scans
- **Deployment**: Podman/Docker, Nginx, multi-stage builds

---

## Quick Start

### 🚀 Containerized Deployment (Recommended)

```bash
git clone https://github.com/jim-wyatt/msn-weather-wrapper.git
cd msn-weather-wrapper
export APP_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
podman-compose -f infra/compose/podman-compose.yml up -d
# Access at http://localhost:8080
```

A prebuilt image is also published to
[GitHub Container Registry](https://github.com/jim-wyatt/msn-weather-wrapper/pkgs/container/msn-weather-wrapper).

### 📦 Python Package

```bash
pip install msn-weather-wrapper
```

```python
from backend import WeatherClient, Location

with WeatherClient() as client:
    location = Location(city="London", country="UK")
    weather = client.get_weather(location)
    print(f"Temperature: {weather.temperature}°C")
```

> **Note:** the distribution is named `msn-weather-wrapper`, but the importable
> package is currently `backend`.

### 🧪 Development Environment

```bash
./dev.sh setup   # One-time setup
./dev.sh start   # Start dev servers
./dev.sh status  # Check health
# Frontend: http://localhost:3000
# API: http://localhost:5000
# Health: http://localhost:5000/api/v1/health
```

### 🧭 Start Here If You're New

If you're learning the codebase, explore it in this order:

1. `backend/` — the weather client, models, and the FastAPI app (`backend/api/`)
2. `frontend/` — the Next.js UI
3. `tests/` — examples of expected behavior
4. `scripts/` — helper commands for setup, reports, and deployment tasks

> A detailed walkthrough now lives in `docs/PROJECT_STRUCTURE.md`.

---

## Features

- 🌤️ Weather data extraction from MSN Weather
- 🌍 463+ cities worldwide with autocomplete
- 🔌 RESTful API with comprehensive validation
- 📚 **Interactive API docs** (Swagger UI at `/apidocs`)
- ⚛️ Modern web interface with Next.js, React, and TypeScript
- 🚀 5-minute caching (90%+ faster repeated requests)
- 🔒 Rate limiting (30 req/min per IP, 200/hr global)
- 🛡️ Input validation & attack prevention (SQL injection, XSS, etc.)
- 🔐 **Automated security scanning** (Bandit, Semgrep, Trivy, Grype)
- 🔍 Type safety with mypy strict mode
- 📋 SBOM generation for supply chain security
- ♿ WCAG 2.1 Level AA accessible frontend
- 🔄 **Modular CI/CD workflows** - Reusable, maintainable architecture
- 🔄 **Optimized CI/CD** with Docker caching & conditional matrices
- 🏷️ **Automated semantic versioning** - Merged PRs are versioned and published to PyPI automatically

---

## Installation

### Prerequisites

- Python 3.10+
- Node.js 24+ (for frontend development)
- Podman or Docker (for containerized deployment)

### From Source

```bash
git clone https://github.com/jim-wyatt/msn-weather-wrapper.git
cd msn-weather-wrapper
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

---

## Usage

### Python Library

```python
from backend import WeatherClient, Location

with WeatherClient() as client:
    location = Location(city="Seattle", country="USA")
    weather = client.get_weather(location)

    print(f"Temperature: {weather.temperature}°C")
    print(f"Condition: {weather.condition}")
    print(f"Humidity: {weather.humidity}%")
```

### REST API

```bash
# Development
APP_ENV=development uvicorn backend.api.main:app --reload --port 5000

# Production (APP_SECRET_KEY is required)
gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 --workers 4 --timeout 120 backend.api.main:app

# GET request
curl "http://localhost:5000/api/v1/weather?city=London&country=UK"

# POST request
curl -X POST http://localhost:5000/api/v1/weather \
  -H "Content-Type: application/json" \
  -d '{"city": "London", "country": "UK"}'
```

### Web Frontend

```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

**Features:** City autocomplete (463+ cities), temperature unit toggle (°C/°F), geolocation support, responsive design, WCAG 2.1 Level AA accessibility

---

## Development

```bash
# Setup & Run
./dev.sh setup   # One-time setup
./dev.sh start   # Start dev environment
./dev.sh test    # Run tests
./dev.sh logs    # View logs

# Code Quality
ruff format .                    # Format
ruff check .                     # Lint
mypy backend                     # Type check
pre-commit run --all-files       # Run all checks

# Testing
pytest                           # All tests
pytest --cov=backend --cov-report=html  # With coverage
pytest tests/test_client.py -v   # Specific file
```

---

## Deployment

```bash
export APP_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"

# Podman/Docker Compose
podman-compose -f infra/compose/podman-compose.yml up -d
podman-compose -f infra/compose/podman-compose.yml logs -f
podman-compose -f infra/compose/podman-compose.yml down

# Standalone Container
podman build -t msn-weather-wrapper -f infra/containers/Containerfile .
podman run -p 8080:80 -e APP_SECRET_KEY msn-weather-wrapper
```

`APP_SECRET_KEY` must be supplied at runtime in production. Set `CORS_ORIGINS` to a
comma-separated list of explicit origins if the API is called cross-origin; see
[.env.example](.env.example) for all settings.

**Architecture:** Unified container (Python + Node.js), Nginx reverse proxy, Gunicorn with Uvicorn workers, and Kubernetes-ready health checks

---

## Documentation

📚 [Full Documentation](https://jim-wyatt.github.io/msn-weather-wrapper/)

- [API Reference](docs/API.md) - Complete REST API documentation
- [Interactive Swagger UI](docs/SWAGGER.md) - Live API testing & exploration
- [Development Guide](docs/DEVELOPMENT.md) - Setup & development workflow
- [Testing Guide](docs/TESTING.md) - Test suite & coverage
- [Security Guide](docs/SECURITY.md) - Security features & automated scanning
- [SBOM Guide](docs/SYFT_GUIDE.md) - Software bill of materials
- [Changelog](docs/CHANGELOG.md) - Version history

---

## Project Structure

```text
msn-weather-wrapper/
├── backend/
│   ├── api/                    # FastAPI app (main, routers, services, schemas)
│   ├── client.py               # Core MSN weather client
│   ├── models.py               # Shared Pydantic models
│   └── exceptions.py           # Domain exceptions
├── frontend/                   # Next.js application
├── tests/                      # Backend and integration tests
├── scripts/                    # Dev, reporting, and deployment helpers
├── infra/                      # Containers, compose files, and runtime config
├── docs/                       # Docs and beginner walkthroughs
├── dev.sh                      # Thin wrapper around `scripts/dev.sh`
└── pyproject.toml              # Python project configuration
```

---

## Contributing

Contributions are welcome! Please ensure:

1. ✅ All tests pass: `pytest`
2. 🎨 Code is formatted: `ruff format .`
3. 🔍 Type checks pass: `mypy backend/`
4. 🪝 Pre-commit hooks pass
5. 📝 Documentation is updated

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines and the
[Code of Conduct](CODE_OF_CONDUCT.md). To report a vulnerability, follow the
[security policy](.github/SECURITY.md) rather than opening a public issue.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Links

- 📖 [Documentation](https://jim-wyatt.github.io/msn-weather-wrapper/)
- 📦 [PyPI Package](https://pypi.org/project/msn-weather-wrapper/)
- 🐛 [Issue Tracker](https://github.com/jim-wyatt/msn-weather-wrapper/issues)
- 🔒 [Security Policy](.github/SECURITY.md)

---

## Disclaimer

This project is an unofficial wrapper for MSN Weather data and is provided for educational and personal use only. It works by parsing public MSN Weather pages, so it can break without notice when the upstream site changes, and you are responsible for complying with the upstream terms of use. This software is not affiliated with, endorsed by, or officially connected to Microsoft Corporation or MSN Weather in any way.

---
