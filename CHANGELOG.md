# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Multi-day weather forecasts
- Weather alerts and notifications
- User accounts with saved locations
- GraphQL API support
- WebSocket real-time updates

## [1.0.0] - 2025-12-02

### Initial Release

**MSN Weather Wrapper v1.0.0** is the first production-ready release, featuring a complete weather data solution with Python library, REST API, and modern web interface.

#### Added
- Python weather client library with type-safe Pydantic models
- Flask REST API with comprehensive endpoints
  - Weather by city (GET/POST)
  - Weather by coordinates with geolocation
  - Health checks (basic, liveness, readiness)
  - Recent searches management
- React 19 + Vite 7 frontend with TypeScript
  - City autocomplete (406+ cities)
  - Temperature unit toggle (Celsius/Fahrenheit)
  - Geolocation support ("Use My Location" button)
  - Recent searches history
  - Responsive mobile-friendly design
- Security features
  - Input validation and sanitization
  - Protection against SQL injection, XSS, path traversal, command injection
  - Rate limiting (30 req/min per IP, 200/hr global)
  - Comprehensive security test suite (25 tests)
- Production deployment
  - Gunicorn WSGI server (4 workers, 120s timeout)
  - Podman containerized deployment
  - Multi-stage Docker builds
  - Nginx reverse proxy
- Development tools
  - Containerized development environment (bootstrap-dev.sh)
  - Hot reload for backend (Flask) and frontend (Vite HMR)
  - Pre-commit hooks (ruff, mypy, pytest)
  - Comprehensive test suite (77 tests, 90% coverage)
- Documentation
  - Complete API reference
  - Security documentation
  - Testing guide
  - Development guide
  - Container development setup
  - SBOM generation guide
- CI/CD ready
  - GitHub Actions workflows
  - Multi-platform container builds
  - SBOM generation with Syft
  - Automated testing and deployment

#### Technology Stack
- **Backend**: Python 3.9+, Flask 3.1+, Gunicorn 23.0+, Pydantic 2.12+
- **Frontend**: React 19.2, Vite 7.2, TypeScript 5.7+
- **Testing**: pytest 9.0+, Playwright, 77 tests with 90% coverage
- **Quality**: ruff 0.14+, mypy 1.19+, pre-commit 4.5+
- **Deployment**: Podman, multi-stage containers, Nginx

---

## Release Notes Guidelines

### Version Format
- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes, backward compatible

### Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

---

Last updated: December 2, 2025
