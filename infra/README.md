# Infrastructure Guide

This folder holds the files needed to **run** the project, not the files that define the app's business logic.

## Layout

- `containers/` — container build definitions for production, development, and Playwright
- `compose/` — Podman/Docker Compose files for local orchestration
- `config/` — nginx and entrypoint configuration used by the containers

## Beginner Tip

If you are changing **application behavior**, you usually do **not** need this folder.

Start in:

- `src/msn_weather_wrapper/` for backend code
- `frontend/` for UI code
- `tests/` for examples of expected behavior

Use `infra/` when you need to change how the app is **built, started, or deployed**.
