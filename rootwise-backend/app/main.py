
from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import (
    health,
    regions,
    fields,
    crops,
    recommendations,
    simulations,
    ingestion,
    climate,
    map_data,
    risk,
    timeseries,
)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "ROOTWISE - Satellite-based agricultural insights "
        "and crop rotation decision support system."
    ),
    version="1.0.0",
)

# Health check
app.include_router(health.router)

# Main API routes
app.include_router(
    regions.router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    fields.router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    crops.router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    recommendations.router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    simulations.router,
    prefix=settings.API_V1_PREFIX,
)

# M2 Data Ingestion API
app.include_router(
    ingestion.router,
    prefix=settings.API_V1_PREFIX,
)
# Climate APIs
app.include_router(
    climate.router,
    prefix=settings.API_V1_PREFIX,
)
# Map APIs
app.include_router(
    map_data.router,
    prefix=settings.API_V1_PREFIX,
)
# Risk APIs
app.include_router(
    risk.router,
    prefix=settings.API_V1_PREFIX,
)

# Time-Series APIs
app.include_router(
    timeseries.router,
    prefix=settings.API_V1_PREFIX,
)

@app.get("/")
def root():
    return {
        "application": "ROOTWISE",
        "message": "ROOTWISE Backend API is running",
        "documentation": "/docs",
        "health": "/health",
    }
