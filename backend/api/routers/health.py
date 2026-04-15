"""Health and readiness routes for the FastAPI service."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.api.schemas import HealthResponse
from backend.api.services import get_client

router = APIRouter(tags=["health"])


@router.get("/v1/health", response_model=HealthResponse)
async def health_check() -> dict[str, str]:
    """Return a basic service health response."""
    return {"status": "ok", "service": "MSN Weather Wrapper API", "version": "1.0"}


@router.get("/v1/health/live", response_model=HealthResponse)
async def liveness_probe() -> dict[str, str]:
    """Return a Kubernetes-friendly liveness probe response."""
    return {"status": "alive", "service": "MSN Weather Wrapper API"}


@router.get("/v1/health/ready", response_model=HealthResponse)
async def readiness_probe() -> JSONResponse:
    """Return the service readiness state and dependency checks."""
    checks: dict[str, bool] = {}
    overall_ready = True
    client = None

    try:
        client = get_client()
        checks["weather_client"] = True
    except Exception:
        checks["weather_client"] = False
        overall_ready = False

    try:
        if client is None:
            raise RuntimeError("weather client unavailable")
        response = client.session.head("https://www.msn.com", timeout=2)
        checks["external_api"] = response.status_code < 500
        if not checks["external_api"]:
            overall_ready = False
    except Exception:
        checks["external_api"] = False
        overall_ready = False

    status_code = 200 if overall_ready else 503
    payload = {
        "status": "ready" if overall_ready else "not_ready",
        "service": "MSN Weather Wrapper API",
        "checks": checks,
    }
    return JSONResponse(content=payload, status_code=status_code)
