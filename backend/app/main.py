# backend/app/main.py
import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.router import router as api_router
from app.core.config import settings
from app.api import api_router

if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.2)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Security & CORS
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(o) for o in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
Instrumentator().instrument(app).expose(app, include_in_schema=False, endpoint="/metrics")

# API V1
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
