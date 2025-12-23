"""
=============================================================================
SMARTCAREER AI - MAIN APPLICATION
=============================================================================

FastAPI application entry point.

FEATURES:
    - API versioning (v1)
    - CORS configuration
    - Health checks
    - Exception handlers
    - Startup/shutdown events

RUN WITH:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

DOCS:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - OpenAPI JSON: http://localhost:8000/openapi.json

=============================================================================
AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

# Local imports
from app.config import settings, print_config_summary
from app.api.v1 import api_router
from app.database import check_database_connection

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


# =============================================================================
# LIFESPAN EVENTS
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    
    Startup:
        - Log configuration
        - Check database connection
        - Initialize services
    
    Shutdown:
        - Close connections
        - Cleanup resources
    """
    # =========================================================================
    # STARTUP
    # =========================================================================
    
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)
    
    # Print configuration summary
    if settings.DEBUG:
        print_config_summary()
    
    # Check database connection
    if check_database_connection():
        logger.info("✅ Database connection successful")
    else:
        logger.error("❌ Database connection failed!")
    
    # Log API info
    logger.info(f"📚 API Documentation: http://localhost:8000/docs")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    logger.info("=" * 60)
    
    yield  # Application runs here
    
    # =========================================================================
    # SHUTDOWN
    # =========================================================================
    
    logger.info("=" * 60)
    logger.info(f"👋 Shutting down {settings.APP_NAME}...")
    logger.info("=" * 60)


# =============================================================================
# APPLICATION FACTORY
# =============================================================================

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI instance
    """
    
    application = FastAPI(
        title=settings.APP_NAME,
        description="""
        ## SmartCareer AI API
        
        AI-powered career platform API for resume generation and job matching.
        
        ### Features
        - 👤 **Authentication**: Register, login, JWT tokens
        - 📄 **Resumes**: Create, edit, AI-generate resumes
        - 💼 **Jobs**: Browse, search, post job listings
        - 📨 **Applications**: Apply to jobs, track status
        
        ### Authentication
        Most endpoints require a Bearer token in the Authorization header:
        ```
        Authorization: Bearer <your_access_token>
        ```
        
        Get a token by calling `POST /api/v1/auth/login`.
        """,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # =========================================================================
    # CORS MIDDLEWARE
    # =========================================================================
    
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # =========================================================================
    # INCLUDE ROUTERS
    # =========================================================================
    
    # API v1
    application.include_router(
        api_router,
        prefix="/api/v1"
    )
    
    return application


# =============================================================================
# CREATE APP INSTANCE
# =============================================================================

app = create_application()


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Returns user-friendly error messages.
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip "body"
        message = error["msg"]
        errors.append({"field": field, "message": message})
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handle database errors.
    
    Logs the actual error but returns generic message to user.
    """
    logger.exception(f"Database error: {exc}")
    
    # Log to error service
    try:
        from app.services.error_logging_service import error_logger, ErrorCategory, ErrorSeverity
        await error_logger.log_database_error(
            error=exc,
            operation="query",
            extra_data={
                "endpoint": request.url.path,
                "method": request.method,
            }
        )
    except Exception as log_error:
        logger.error(f"Failed to log error: {log_error}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "A database error occurred. Please try again later."
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle unexpected errors.
    
    Logs the error and returns a generic message.
    """
    logger.exception(f"Unexpected error: {exc}")
    
    # Log to error service
    try:
        from app.services.error_logging_service import error_logger, ErrorCategory, ErrorSeverity
        await error_logger.log_api_error(
            error=exc,
            endpoint=request.url.path,
            method=request.method,
            status_code=500,
            ip_address=request.client.host if request.client else None,
        )
    except Exception as log_error:
        logger.error(f"Failed to log error: {log_error}")
    
    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later."
        }
    )


# =============================================================================
# ROOT ENDPOINTS
# =============================================================================

@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
    response_model=Dict[str, Any]
)
async def root():
    """
    Root endpoint - returns API info.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api": "/api/v1"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    response_model=Dict[str, Any]
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        - status: "healthy" or "unhealthy"
        - database: connection status
        - version: app version
    """
    db_healthy = check_database_connection()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": settings.APP_VERSION,
    }


@app.get(
    "/api",
    tags=["Health"],
    summary="API info",
    response_model=Dict[str, Any]
)
async def api_info():
    """
    API information endpoint.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "resumes": "/api/v1/resumes",
            "jobs": "/api/v1/jobs",
            "applications": "/api/v1/applications",
        }
    }


# =============================================================================
# RUN DIRECTLY (for development)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug" if settings.DEBUG else "info"
    )
