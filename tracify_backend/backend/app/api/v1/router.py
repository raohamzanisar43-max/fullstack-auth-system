"""
API v1 Router for Tracerfy Backend
"""

from fastapi import APIRouter
from typing import List

# Import route modules
from app.api.v1 import auth, api_keys, traces, credits, dashboard, dnc

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["API Keys"])
api_router.include_router(traces.router, prefix="/traces", tags=["Trace Jobs"])
api_router.include_router(credits.router, prefix="/credits", tags=["Credits"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(dnc.router, prefix="/dnc", tags=["DNC Scrubbing"])

# Placeholder for health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Tracerfy API is running"}

# Placeholder for root endpoint
@api_router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "name": "Tracerfy API",
        "version": "1.0.0",
        "description": "Professional Skip Tracing Services for Real Estate & Lead Generation"
    }
