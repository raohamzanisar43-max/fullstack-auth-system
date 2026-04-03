"""
Tracerfy Backend - Main Application Entry Point
Professional Skip Tracing Platform for Real Estate Lead Generation
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.exceptions import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitExceeded,
    PaymentError,
    DNCServiceError
)
from app.db.session import engine, Base
from app.api.v1.router import api_router
from app.middleware.auth import (
    create_auth_middleware,
    create_api_key_middleware,
    create_role_middleware,
    create_tenant_middleware
)
from app.middleware.logging import (
    create_logging_middleware,
    create_structured_logging_middleware
)
from app.middleware.rate_limit import (
    create_rate_limit_middleware,
    create_advanced_rate_limit_middleware
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log", encoding="utf-8") if settings.ENVIRONMENT == "production" else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Tracerfy Backend...")
    
    try:
        # Initialize database (optional for now)
        # await initialize_database()
        
        # Initialize background services
        # await initialize_background_services()
        
        # Health check
        # await health_check()
        
        logger.info("✅ Tracerfy Backend started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to start Tracerfy Backend: {str(e)}")
        # Don't raise - allow app to start anyway
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Tracerfy Backend...")
    
    try:
        # Cleanup background services
        await cleanup_background_services()
        
        # Close database connections
        await cleanup_database()
        
        logger.info("✅ Tracerfy Backend shut down successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="Tracerfy API",
    description="Professional Skip Tracing Services for Real Estate & Lead Generation\n\n"
                "Find property owners, locate homeowners, and generate real estate leads "
                "with our comprehensive skip tracing platform. Starting at just $0.02 per lead!",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
    contact={
        "name": "Tracerfy Support",
        "email": "support@tracerfy.com",
        "url": "https://www.tracerfy.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": str(exc),
            "type": "validation_error",
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors"""
    logger.warning(f"Authentication error: {str(exc)}")
    return JSONResponse(
        status_code=401,
        content={
            "error": "Authentication Error",
            "message": str(exc),
            "type": "authentication_error",
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.exception_handler(AuthorizationError)
async def authorization_exception_handler(request: Request, exc: AuthorizationError):
    """Handle authorization errors"""
    logger.warning(f"Authorization error: {str(exc)}")
    return JSONResponse(
        status_code=403,
        content={
            "error": "Authorization Error",
            "message": str(exc),
            "type": "authorization_error",
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    """Handle not found errors"""
    logger.info(f"Not found error: {str(exc)}")
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": str(exc),
            "type": "not_found_error",
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit errors"""
    logger.warning(f"Rate limit exceeded: {str(exc)}")
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate Limit Exceeded",
            "message": str(exc),
            "type": "rate_limit_exceeded",
            "retry_after": getattr(exc, 'retry_after', 60),
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.exception_handler(PaymentError)
async def payment_exception_handler(request: Request, exc: PaymentError):
    """Handle payment errors"""
    logger.error(f"Payment error: {str(exc)}")
    return JSONResponse(
        status_code=402,
        content={
            "error": "Payment Error",
            "message": str(exc),
            "type": "payment_error",
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.exception_handler(DNCServiceError)
async def dnc_service_exception_handler(request: Request, exc: DNCServiceError):
    """Handle DNC service errors"""
    logger.error(f"DNC service error: {str(exc)}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "DNC Service Error",
            "message": str(exc),
            "type": "dnc_service_error",
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "type": "internal_server_error",
            "timestamp": asyncio.get_event_loop().time()
        }
    )


# Middleware setup
def setup_middleware():
    """Configure application middleware"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware (production)
    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )
    
    # Logging middleware
    if settings.STRUCTURED_LOGGING:
        app.add_middleware(create_structured_logging_middleware)
    else:
        app.add_middleware(create_logging_middleware, log_level=settings.LOG_LEVEL)
    
    # Rate limiting middleware
    if settings.ENABLE_RATE_LIMITING:
        if settings.ADVANCED_RATE_LIMITING:
            app.add_middleware(
                create_advanced_rate_limit_middleware,
                redis_url=settings.REDIS_URL,
                default_limits={
                    "default": (100, 60),
                    "auth": (10, 60),
                    "upload": (5, 60),
                    "trace": (20, 60),
                    "api": (1000, 60),
                    "admin": (200, 60),
                }
            )
        else:
            app.add_middleware(
                create_rate_limit_middleware,
                redis_url=settings.REDIS_URL
            )
    
    # Authentication middleware
    public_paths = [
        "/",
        "/health",
        "/metrics",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon.ico",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/api/v1/auth/forgot-password",
        "/api/v1/auth/reset-password",
        "/api/v1/webhooks/stripe",  # Stripe webhooks
    ]
    
    app.add_middleware(create_auth_middleware, public_paths=public_paths)
    app.add_middleware(create_api_key_middleware)
    app.add_middleware(create_role_middleware)
    app.add_middleware(create_tenant_middleware)


# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Health check endpoints
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Tracerfy API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs" if settings.ENVIRONMENT != "production" else "Documentation not available in production"
    }


@app.get("/health", tags=["Health"])
async def health_check_endpoint():
    """Detailed health check"""
    health_status = await get_health_status()
    return health_status


@app.get("/metrics", tags=["Health"])
async def metrics():
    """Application metrics (for monitoring)"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    return {
        "timestamp": asyncio.get_event_loop().time(),
        "memory": {
            "rss": process.memory_info().rss,
            "vms": process.memory_info().vms,
            "percent": process.memory_percent()
        },
        "cpu": {
            "percent": process.cpu_percent()
        },
        "threads": process.num_threads(),
        "connections": len(process.connections())
    }


# Database and service initialization
async def initialize_database():
    """Initialize database tables"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise


async def initialize_background_services():
    """Initialize background services"""
    try:
        # Initialize Celery workers (if configured)
        if settings.ENABLE_CELERY:
            from app.workers.celery_app import celery_app
            # Celery workers are started separately
            logger.info("✅ Celery configuration loaded")
        
        # Initialize Redis connection (if configured)
        if settings.REDIS_URL:
            import redis
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            logger.info("✅ Redis connection established")
        
        # Initialize integrations
        if settings.STRIPE_SECRET_KEY:
            from app.integrations.payment_gateway import payment_gateway
            logger.info("✅ Payment gateway initialized")
        
        if all([
            hasattr(settings, 'FEDERAL_DNC_API_URL'),
            hasattr(settings, 'STATE_DNC_API_URL'),
            hasattr(settings, 'DMA_API_URL'),
            hasattr(settings, 'TCPA_LITIGATOR_API_URL')
        ]):
            from app.integrations.dnc_registry import dnc_registry
            logger.info("✅ DNC registry initialized")
        
    except Exception as e:
        logger.error(f"❌ Background services initialization failed: {str(e)}")
        # Don't raise - allow app to start without optional services


async def cleanup_background_services():
    """Cleanup background services"""
    try:
        # Close Redis connection
        if settings.REDIS_URL:
            # Redis connections are managed by connection pools
            logger.info("✅ Redis connections cleaned up")
        
        # Other cleanup tasks...
        
    except Exception as e:
        logger.error(f"❌ Background services cleanup failed: {str(e)}")


async def cleanup_database():
    """Cleanup database connections"""
    try:
        await engine.dispose()
        logger.info("✅ Database connections closed")
        
    except Exception as e:
        logger.error(f"❌ Database cleanup failed: {str(e)}")


async def health_check():
    """Perform health check"""
    health_status = await get_health_status()
    
    if not health_status["healthy"]:
        raise Exception("Health check failed")


async def get_health_status() -> dict:
    """Get detailed health status"""
    status = {
        "healthy": True,
        "timestamp": asyncio.get_event_loop().time(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "services": {}
    }
    
    # Check database
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        status["services"]["database"] = {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        status["services"]["database"] = {"status": "unhealthy", "message": str(e)}
        status["healthy"] = False
    
    # Check Redis (if configured)
    if settings.REDIS_URL:
        try:
            import redis
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            status["services"]["redis"] = {"status": "healthy", "message": "Redis connection successful"}
        except Exception as e:
            status["services"]["redis"] = {"status": "unhealthy", "message": str(e)}
            status["healthy"] = False
    
    # Check external services
    if settings.STRIPE_SECRET_KEY:
        try:
            from app.integrations.payment_gateway import payment_gateway
            status["services"]["payment_gateway"] = {"status": "healthy", "message": "Payment gateway available"}
        except Exception as e:
            status["services"]["payment_gateway"] = {"status": "unhealthy", "message": str(e)}
    
    return status


# Setup middleware
setup_middleware()


if __name__ == "__main__":
    """Run the application directly"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        use_colors=True
    )
