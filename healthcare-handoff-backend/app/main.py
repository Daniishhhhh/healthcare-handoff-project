"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging
import os

from app.config import settings
from app.db.database import engine
from app.db.base import Base
from app.exceptions import BaseAPIException
from app.auth.routes import router as auth_router
from app.api.v1.patients import router as patients_router
from app.api.v1.handoffs import router as handoffs_router
from app.api.v1.items import router as items_router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Healthcare Handoff Management Backend",
        debug=settings.debug,
    )

    Base.metadata.create_all(bind=engine)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3001", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(BaseAPIException)
    async def api_exception_handler(request, exc: BaseAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc: ValidationError):
        errors = {}
        for error in exc.errors():
            field = ".".join(str(x) for x in error["loc"][1:])
            errors[field] = error["msg"]

        return JSONResponse(
            status_code=422,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": errors,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
            },
        )

    # Include routers
    app.include_router(auth_router)
    app.include_router(patients_router)
    app.include_router(handoffs_router)
    app.include_router(items_router)

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down application")

    return app


app = create_app()