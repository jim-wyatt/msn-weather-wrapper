# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Modular FastAPI backend structure**
  - New `backend/msn_weather_wrapper/api/` package with `main.py`, `routers/`, `services.py`, `schemas.py`, and `config.py`
  - Beginner-friendly backend and structure guides in `backend/msn_weather_wrapper/api/README.md`, `docs/PROJECT_STRUCTURE.md`, and `infra/README.md`

### Changed
- **Backend framework and repo layout**
  - Refactored the monolithic Flask API into a FastAPI-based structure while keeping `api.py` as a compatibility entrypoint
  - Reorganized the repository to be easier to navigate: deployment assets now live under `infra/` and developer utilities under `scripts/`
  - Updated container, workflow, and documentation references to match the new layout

### Fixed
- **Developer workflow and live parsing**
  - Restored live MSN weather parsing with a more resilient fallback for the current upstream page structure
  - Corrected compose/container paths after the repository cleanup and resolved editor diagnostics in the FastAPI test compatibility layer

## [2.0.2] - 2026-04-02

### Fixed
- **Release automation reliability**
  - Auto-versioning now reads the latest git tag correctly and avoids version-bump loops
  - Addressed release workflow edge cases found during code review

- **Container security hardening**
  - Removed `gcc` and `supervisor` from the final production image to eliminate roughly 63 high-severity CVEs
  - Reduced the runtime image footprint and simplified the final container stage

### Changed
- **Operational stability**
  - Hardened the automated release path and production image configuration for safer deployments

## [1.9.17] - 2026-04-02

### Added
- **Client and monitoring improvements**
  - Async weather client support with retry logic and more granular exception handling
  - Compact monitor/dashboard updates optimized for smaller terminal layouts
  - Node.js 22 LTS adoption for monitoring and frontend tooling support

### Changed
- **Dependency and tooling refresh**
  - Updated frontend/tooling dependencies across the React, Vite, and GitHub Actions ecosystem
  - Refined container base-image choices and pinned versions to improve build stability and scan results
  - Continued CI/CD maintenance across the 1.9.x line, including test filtering and release workflow cleanup

### Fixed
- **Compatibility and maintenance**
  - TypeScript 6 compatibility for the existing frontend path mapping
  - Vite 8 and `@vitejs/plugin-react` alignment issues
  - Code scanning findings, failing tests, safety scanner command changes, broken docs links, and auto-version permission issues

## [1.9.0] - 2025-12-05

### Added
- **Automated versioning and monitoring enhancements**
  - PR-based auto-versioning and release flow improvements
  - More compact CI/monitor output with better job-level visibility
  - Broader documentation consolidation and navigation cleanup

### Changed
- **Platform and workflow maintenance**
  - Container base images were refreshed and standardized during the 1.9.0 rollout
  - Development and monitoring workflows were tuned for clearer output and easier maintenance

### Fixed
- Broken documentation links and protected-branch issues in the auto-version workflow

## [1.8.0] - 2025-12-04

### Added
- **Modular CI/CD Workflow Architecture**
  - Refactored monolithic `ci.yml` (662 lines) into modular reusable workflows
  - Created `test.yml` for all testing phases (smoke, unit, coverage, integration)
  - Created `security.yml` for security scanning (basic and full scan modes)
  - Created `build.yml` for Docker builds, SBOM generation, and documentation
  - Created `deploy.yml` for report generation and GitHub Pages deployment
  - Updated `performance.yml` to support workflow_call for reusability
  - Main `ci.yml` now orchestrates workflows (reduced to ~120 lines)
  - Improved maintainability, modularity, and separation of concerns
  - Enhanced workflow diagram documentation with modular architecture

- **OpenAPI/Swagger Documentation**
  - Interactive API documentation at `/apidocs/`
  - Complete OpenAPI 2.0 specification at `/apispec.json`
  - All 11 endpoints documented with schemas and examples
  - "Try it out" feature for live API testing
  - Flasgger integration for auto-generated docs

- **Enhanced CI/CD Pipeline**
  - Composite action for Python environment setup (reduces duplication)
  - Path-based workflow triggers (only run relevant tests)
  - Conditional test matrices (PR: Python 3.12 only, push: 3.10-3.12)
  - Smoke tests for fast-fail validation (30 seconds)
  - Docker image artifact sharing between workflows (saves 2-3 min/workflow)
  - Consolidated security scanning workflow (`security-scan.yml`)
  - Optimized artifact retention policies (40% storage cost reduction)

- **Automated Security Scanning**
  - Weekly security scans (Mondays 2 AM UTC) + on main branch pushes
  - SAST tools: Bandit (Python security), Semgrep (pattern detection)
  - Dependency scanning: pip-audit
  - Container security: Trivy, Grype (image vulnerabilities)
  - License compliance: pip-licenses check
  - Results uploaded to GitHub Security tab

### Improved
- **CORS Configuration**
  - Dual-layer CORS (Flask + Nginx)
  - Dynamic origin handling for flexible deployment
  - Credentials support for session-based features
  - Preflight OPTIONS request handling
  - Documented in API.md with examples

- **Documentation**
  - New dedicated Swagger UI guide (`SWAGGER.md`)
  - Enhanced API.md with interactive documentation section
  - Security.md updated with automated scanning details
  - Index.md reflects new features and statistics
  - MkDocs navigation includes Swagger documentation

- **Code Quality**
  - Configured Ruff isort with `known-first-party` for proper import organization
  - Pre-commit hooks configured and installed
  - Integration tests validate CORS headers in containerized deployment

### Fixed
- CORS headers missing in Nginx proxy for containerized deployments
- Ruff import organization (I001) errors with local package imports
- Docker layer caching improvements for faster builds

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
  - **Zero vulnerabilities** (verified with pip-audit, bandit, Grype)

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
- **Security**: pip-audit 2.10+, Grype 0.104+, Trivy
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

Last updated: April 3, 2026
