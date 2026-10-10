# Project Structure Guide

This repository is organized so a beginner can reason about it in **four main zones**.

## Start Here

If you're new, explore the project in this order:

1. `backend/` — the Python backend and library code
2. `frontend/` — the Next.js user interface
3. `tests/` — examples of how behavior is verified
4. `scripts/` — helper scripts for local development and reporting

## Mental Model

### `backend/`

This is the **main backend code**.

- `api/` — FastAPI app (`main.py`), routes (`routers/`), request handling, and service logic
- `client.py` — talks to MSN Weather
- `models.py` — shared typed data models
- `exceptions.py` — app-specific errors

### `frontend/`

This is the **web app**.

- `app/` — Next.js App Router source (layout, page, components, data, types, CSS)
- `tests/e2e/` — Playwright browser tests
- `next.config.ts` — Next.js configuration (API rewrites, standalone output)

### `tests/`

This is the **backend test suite**.

- `test_api.py` — API behavior
- `test_client.py` — weather client behavior
- `test_models.py` — data model validation
- `test_security.py` — input validation and security checks
- `test_integration.py` — checks against the running container
- `test_benchmarks.py` — performance benchmarks

### `scripts/`

This is the **developer toolbox**.

- `dev.sh` — start, stop, test, and inspect the local dev stack
- `generate_reports.py` — build markdown reports from CI/test artifacts
- `generate_sbom.sh` — software bill of materials generation

### `infra/`

This is the **deployment and container area**.

- `containers/` — production/dev/test container definitions
- `compose/` — local orchestration files
- `config/` — nginx and entrypoint configuration

### `docs/`

This is the **project documentation**.

Use it when you want explanations, not implementation details.

## Top-Level Map

```text
msn-weather-wrapper/
├── backend/                  # Backend/library code
├── frontend/                 # Next.js UI
├── tests/                    # Python tests
├── scripts/                  # Dev and automation scripts
├── infra/                    # Container and deployment config
├── docs/                     # Documentation
├── dev.sh                    # Simple wrapper around scripts/dev.sh
└── pyproject.toml            # Python project config
```

## Rule of Thumb

> If you want to **change behavior**, start in `backend/`.
> If you want to **change UI**, go to `frontend/`.
> If you want to **understand intent**, read `tests/` and `docs/`.
