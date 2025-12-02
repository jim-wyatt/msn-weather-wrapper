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
- **Python Weather Client Library**
  - Type-safe Pydantic models for weather data
  - Context manager support for session management
  - Celsius/Fahrenheit temperature conversion
  - Automatic HTML and JSON parsing
  - Comprehensive error handling

- **REST API with Flask**
  - Weather by city (GET/POST): `/api/weather`, `/api/v1/weather`
  - Weather by coordinates with geolocation: `/api/weather/coordinates`
  - Health checks: `/health`, `/healthz` (liveness), `/readyz` (readiness)
  - Recent searches management: GET, DELETE
  - API versioning support (v1)
  - 5-minute response caching
  - Structured JSON logging with structlog
  - Request ID tracing

- **Modern Web Frontend**
  - React 19.2 + TypeScript 5.7 + Vite 7.2
  - City autocomplete (406+ cities worldwide)
  - Temperature unit toggle (Celsius/Fahrenheit)
  - Geolocation support ("Use My Location" button)
  - Recent searches history
  - Responsive mobile-friendly design
  - **Accessibility (WCAG 2.1 Level AA)**
    - ARIA labels and roles throughout
    - Semantic HTML structure
    - Keyboard navigation support
    - Screen reader optimized
    - High-contrast focus indicators
  - **SEO & PWA Features**
    - Comprehensive meta tags
    - Open Graph social sharing
    - Twitter Card support
    - Custom favicon and icons
    - PWA manifest

- **Security Features**
  - Input validation and sanitization
  - Protection against SQL injection, XSS, path traversal, command injection
  - Rate limiting (30 req/min per IP, 200/hr global)
  - CORS configuration
  - Comprehensive security test suite (25 tests)
  - **Zero vulnerabilities** (verified with pip-audit, safety, bandit, Grype)

- **Production Deployment**
  - Gunicorn WSGI server (4 workers, 120s timeout)
  - Podman/Docker containerized deployment
  - Multi-stage builds (reduced image size)
  - Multi-platform support (amd64, arm64)
  - Nginx reverse proxy configuration
  - Health check endpoints for orchestration

- **Development Tools**
  - Containerized development environment (dev.sh)
  - Hot reload for backend (Flask) and frontend (Vite HMR)
  - Pre-commit hooks (ruff, mypy, pytest)
  - Comprehensive test suite (86 tests, 89% coverage)
  - Integration tests for containerized deployments

- **Documentation**
  - Complete API reference with error codes, rate limiting, examples
  - Security documentation and best practices
  - Testing guide with coverage reporting
  - Development guide
  - Container development setup
  - SBOM generation guide
  - MkDocs documentation site with GitHub Pages deployment
  - Versioning and release guide
  - CI/CD pipeline documentation

- **CI/CD Pipeline**
  - GitHub Actions workflows for testing, building, and deployment
  - Multi-platform container builds (linux/amd64, linux/arm64)
  - SBOM generation with Syft
  - Security scanning with Trivy and Grype
  - Automated PyPI publishing on release tags
  - Semantic versioning enforcement
  - Container registry publishing to ghcr.io
  - Automated GitHub releases with artifacts

- **Quality Assurance**
  - 155 dependencies verified MIT-compatible
  - License report generated and reviewed
  - Zero known security vulnerabilities
  - 89% test coverage maintained
  - Type safety with mypy strict mode
  - Code quality with ruff linter
  - All tests passing (69 unit/integration, 17 container tests)

#### Technology Stack
- **Backend**: Python 3.10-3.12, Flask 3.1+, Gunicorn 23.0+, Pydantic 2.12+
- **Frontend**: React 19.2, Vite 7.2, TypeScript 5.7+, CSS3
- **Testing**: pytest 9.0+, Playwright 1.49+, 86 tests with 89% coverage
- **Quality**: ruff 0.14+, mypy 1.19+, pre-commit 4.5+, bandit 1.9+
- **Security**: pip-audit 2.10+, safety 3.7+, Grype 0.104+, Trivy
- **Deployment**: Podman/Docker, multi-stage containers, Nginx, Supervisor
- **Documentation**: MkDocs 1.6+ with Material theme 9.7+
- **CI/CD**: GitHub Actions, Syft SBOM generation, semantic versioning

#### Performance
- 5-minute response caching (90%+ speedup for repeated queries)
- Optimized frontend bundle: 215.98 KB (66.78 KB gzipped)
- Gunicorn worker configuration tuned for production
- Efficient HTML/JSON parsing with Beautiful Soup 4
- Rate limiting prevents abuse while maintaining usability

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
