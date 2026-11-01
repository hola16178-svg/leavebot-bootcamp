"""Application entry point."""

from pathlib import Path
from contextlib import asynccontextmanager
import os
import sqlite3
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from . import db
from .api import register_routes
from .clock import build_today_provider
from .settings import load_settings
from .errors import DomainError, error_body


def create_app(*, db_path=None, today_provider=None, seed_employees=None) -> FastAPI:
    # Resolve configuration at lifespan entry, never open a DB during import.
    @asynccontextmanager
    async def lifespan(application):
        application.state.settings = load_settings(db_path=db_path)
        application.state.today_provider = (
            today_provider if today_provider is not None
            else build_today_provider(os.environ.get("LEAVEBOT_TODAY"))
        )
        employees = seed_employees if seed_employees is not None else [
            {"id": 1, "name": "員工A"}, {"id": 2, "name": "員工B"},
            {"id": 3, "name": "員工C"},
        ]
        db.init_db(application.state.settings.db_path, employees)
        mode = "injected" if today_provider is not None else (
            "environment" if os.environ.get("LEAVEBOT_TODAY") is not None else "local-date"
        )
        logging.getLogger("uvicorn.error").info(
            "Clock mode=%s today=%s", mode, application.state.today_provider().isoformat()
        )
        yield

    application = FastAPI(title="LeaveBot", lifespan=lifespan)

    @application.exception_handler(DomainError)
    async def domain_error(request, exc):
        return JSONResponse(error_body(exc.code, exc.field), status_code=exc.status)

    @application.exception_handler(sqlite3.Error)
    async def storage_error(request, exc):
        logging.getLogger(__name__).error("DB_UNAVAILABLE %s %s", request.url.path, type(exc).__name__)
        return JSONResponse(error_body("DB_UNAVAILABLE"), status_code=503)

    @application.exception_handler(Exception)
    async def internal_error(request, exc):
        logging.getLogger(__name__).error("INTERNAL_ERROR %s %s", request.url.path, type(exc).__name__)
        return JSONResponse(error_body("INTERNAL_ERROR"), status_code=500)

    register_routes(application, lambda: application.state.settings,
                    lambda: application.state.today_provider())

    # Register API routes before the catch-all static page mount.
    application.mount(
        "/", StaticFiles(directory=Path(__file__).parent / "static", html=True),
        name="static",
    )
    return application


app = create_app()
