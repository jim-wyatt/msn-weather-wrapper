# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### ⚠️ Breaking
- **Container runs unprivileged on port 8080**
  - Every process in the published image (nginx, Next.js, gunicorn) now runs as user `app` (uid 10001) and nginx listens on port **8080** instead of 80. Update port mappings from `-p 8080:80` to `-p 8080:8080`; the compose file is already updated. The image needs no Linux capabilities and works with `--cap-drop ALL --security-opt no-new-privileges`
- **Container and API configuration hardening**
  - `APP_SECRET_KEY` is no longer generated at image build time (every pull of the published image shared the same key). It must now be supplied at runtime when `APP_ENV=production`, e.g. `podman run -e APP_SECRET_KEY=...`; the container exits at startup without it
  - `CORS_ORIGINS=*` is rejected at startup. List explicit origins (comma-separated), or leave it unset for same-origin deployments. The image no longer defaults to `*`
  - Nginx no longer reflects the request `Origin` or answers preflights itself; CORS is handled only by FastAPI, so cross-origin callers must be listed in `CORS_ORIGINS`

### Fixed
- The release workflow is hands-free when a `RELEASE_TOKEN` secret exists: it opens the version-bump pull request (so CI runs on it), merges it, and pushes the tag with that token so the publish and container-image runs trigger natively; without the secret it now stops before any half-finished state with the exact recovery commands
- Frontend accessibility: the page now has a `<main>` landmark, headings no longer skip from h1 to h3, recent searches are a real list, the location and unit-toggle buttons' accessible names include their visible text, `aria-activedescendant` is only set while the suggestion list is open, and the brand and secondary text colours meet WCAG AA (7:1 for body text) on white; axe reports no violations on the homepage or after a search
- The Playwright suite runs again: the visual and accessibility specs were still written for a "Get Weather" button that the autocomplete UI removed; they now select a city from the suggestions, mock the weather API so screenshots and scans are deterministic, and the config honours `PORT` so a second checkout can run alongside another dev server. Visual baselines regenerated
- Removed deprecated API usage: gunicorn now loads the worker from the `uvicorn-worker` package (the `uvicorn.workers` module is deprecated), the test client uses `httpx2` on Python 3.11+ as Starlette now expects and sends raw bodies as `content=`, the report generator uses timezone-aware `datetime.now(timezone.utc)` instead of `utcnow()`, and pytest-asyncio's fixture loop scope is set explicitly
- The release trigger now looks up the pull request that produced the merged commit instead of the most recently created merged PR, which after a release was the version-bump PR itself; every second release was being skipped
- The release workflow now dispatches the CI pipeline on the new tag so the versioned container image (`X.Y.Z`, `X.Y`, `X`, `latest`) is published; tags pushed with the workflow token never triggered it, so 2.0.14 shipped without an image tag

### Documentation
- Refreshed the README (security gates, endpoint table, health checks, supply chain) and corrected the city count to the 406 entries in the autocomplete data
- Documentation accuracy pass: dev-server commands now set `APP_ENV=development`, Node.js 26 / Python 3.15 and current dependency versions everywhere, the CI test matrix, the security-report gate tests, the full scripts list, and the session-cookie wording for recent searches
- Corrected the README, contributor guide, and docs site to match the current layout: the importable package is `backend`, the ASGI app is `backend.api.main:app`, routes live under `/api/v1/`, and compose files and Containerfiles live under `infra/`
- Removed stale test counts, coverage figures, and references to files and workflows that no longer exist
- Refreshed the security policy, CODEOWNERS, package metadata, pre-commit hook versions, and Dependabot grouping

### Changed
- **CI caches what it used to rebuild every run.** The Grype vulnerability database is cached per day (it was downloaded fresh on every run, about a minute, the longest step in the container job after the build), the installed Python environment is cached per dependency-file hash and interpreter build so the ten jobs that need it skip the install on a hit, and Semgrep is pinned in `.github/requirements/semgrep.txt` (Dependabot keeps it current) with its pipx environment cached per version
- **CI/CD streamlined into one pipeline.** The container image is built once per run and that build is scanned, smoke-tested, integration-tested and pushed (it used to be built three times); the reusable test/security/build/deploy workflows and the version-bump workflow are gone. Performance tests run weekly instead of on every merge
- **The version is the git tag.** `pyproject.toml` declares a dynamic version resolved by hatch-vcs, `backend.__version__` reads the installed metadata, the image gets it as `APP_VERSION`, and the health endpoint reports it. A green `main` run tags the release itself (`RELEASE_TOKEN`) and the tag runs a short publish workflow; there is no bump commit or bump pull request any more, and merges that change only documentation, CI or tooling are not released
- Runtimes and tooling moved to current stable/LTS lines: Python 3.15 in CI and the container images (the library still supports 3.10+ and is now tested on 3.10 through 3.15), Node.js 26 LTS, npm 12, pip 26.3, and the latest ruff, mypy, and pre-commit hooks. Runtime dependency floors in `pyproject.toml` were raised to the current minor lines; dev-tool floors stay where they were so the dev extra still installs on 3.10.

### Security
- The image lock file is now resolved for the image's own interpreter (Python 3.15 on Linux) instead of universally; the universal lock kept a Python 3.10-only `soupsieve` 3.x pin that carried GHSA-mmhr-3c5m-f64f even though the image never installed it
- Supply chain: the container image installs Python dependencies from a hash-pinned `requirements.txt` (`pip install --require-hashes`, verified with `pip check`) and the frontend with `npm ci --ignore-scripts`; the weekly dependency workflow regenerates the lock
- `APP_SECRET_KEY_FILE` lets the session secret be read from a mounted secret file instead of the environment; production rejects keys shorter than 32 characters
- nginx enforces an edge rate limit (20 req/s per client, burst 40, 429 beyond) and a per-client connection cap, and gunicorn only trusts proxy headers from loopback; nginx access and error logs now go to the container's stdout/stderr
- Hardening pass: nginx now sends `Content-Security-Policy`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy` and `server_tokens off`, hides `X-Powered-By`, and limits request bodies; the API sets `X-Content-Type-Options`, `X-Frame-Options` and `Referrer-Policy` on every response (covered by tests); Next.js no longer sends `X-Powered-By`
- All third-party GitHub Actions are pinned to commit SHAs with version comments (Dependabot keeps them current), and checkouts that never push no longer persist the workflow token
- Updated Next.js to 16.4 and refreshed transitive frontend dependencies (`sharp`, `postcss`, `nanoid`, `baseline-browser-mapping`) to clear outstanding advisories
- Updated the pinned `pip` in the container image to 26.2.1
- Bandit, Semgrep, and pip-audit results now fail the security workflow instead of being ignored
- Semgrep is installed in an isolated pipx environment in CI so that its own pinned transitive dependencies (`mcp`, `opentelemetry-*`) are no longer counted by pip-audit against the project
- Refreshed the pinned `python:3.12-slim-trixie` and `node:24-trixie-slim` base image digests, which carried fixed interpreter CVEs, and enabled Dependabot's docker updater for the Containerfiles so the pins keep moving
- The container security job now also fails on fixable CRITICAL findings from Grype on every pipeline; Grype version-scans the interpreter binaries that Trivy does not
- Removed `curl` from the runtime image; the container and compose health checks now use the bundled Python interpreter
- Bumped `pypa/gh-action-pypi-publish` to 1.14.3 (GHSA-5xjx-3w67-w9x9) and `docker/login-action` to 4.7.0
- Dependabot's docker updater is limited to digest and patch updates on the pinned Python and Node tag lines, so major/minor image jumps stay deliberate

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
- **Modular Workflow Architecture**
  - Refactored monolithic ci.yml (662 lines) into reusable workflows (120 lines)
  - New reusable workflows: test.yml, security.yml, build.yml, deploy.yml
  - Performance.yml updated to support workflow_call trigger
  - Main ci.yml now orchestrates all workflows with clear separation of concerns
  - Reduced code duplication and improved maintainability

- **Enhanced Documentation Organization**
  - Moved workflow documentation to dedicated "CI/CD & Workflows" section
  - Workflow Architecture (WORKFLOW_DIAGRAM.md) promoted to main documentation
  - Automated Versioning and Versioning Guide organized under CI/CD section
  - Reports section reorganized with CI/CD Status at the top

- **Improved Report Generation**
  - Consistent report formatting across all report types
  - Standardized headers with auto-generated timestamps
  - Cross-linking between related reports
  - Enhanced CI/CD status report with workflow architecture overview
  - Unified footer format across all reports

### Changed
- **Workflow Organization**
  - CI/CD pipeline split into modular, reusable components
  - Workflows can be called by multiple other workflows
  - Independent workflows can be tested and triggered manually
  - Improved parallel execution and resource optimization

- **Documentation Structure**
  - MkDocs navigation updated with "CI/CD & Workflows" section
  - Reports page shows CI/CD Status first (was last)
  - All reports link to related documentation consistently

### Improved
- **Maintainability**
  - Simplified main CI/CD workflow (81% reduction in lines)
  - Clear separation between orchestration and execution
  - Easier to add new workflow steps or modify existing ones
  - Better visibility into pipeline structure

- **Developer Experience**
  - Workflow documentation more prominent in navigation
  - Easier to understand CI/CD architecture with visual diagrams
  - Report generation consistent across all types

## [1.7.11] - 2025-12-03

### Added
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
