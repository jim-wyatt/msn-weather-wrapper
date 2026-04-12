# Backend API Guide

This folder contains the **FastAPI backend**.

## Beginner Map

- `main.py` — creates the app and wires middleware + routers together
- `routers/health.py` — health and readiness endpoints
- `routers/weather.py` — weather and recent-search endpoints
- `services.py` — shared helpers like caching, validation, and client access
- `schemas.py` — request/response models

## Rule of Thumb

- Adding a new endpoint? Start in `routers/`
- Changing shared backend behavior? Start in `services.py`
- Changing app setup or middleware? Start in `main.py`
