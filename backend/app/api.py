"""HTTP boundary; database connections live entirely in a worker thread."""
import json
import re

from fastapi import Request
from starlette.concurrency import run_in_threadpool

from . import db, repository, leave_service
from .errors import DomainError
from .schemas import parse_leave


def validate_query(request, allowed):
    unknown = sorted(set(request.query_params) - set(allowed))
    if unknown:
        raise DomainError("UNKNOWN_FIELD", unknown[0])


def register_routes(app, settings, today_provider):
    # settings is a provider: lifespan resolves environment/overrides before use.
    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/employees")
    def employees(request: Request):
        validate_query(request, ())
        with db.connect(settings().db_path) as conn:
            return {"employees": repository.list_employees(conn)}

    def submit_sync(value):
        with db.connect(settings().db_path) as conn:
            return {"leave": leave_service.submit_leave(conn, value)}

    @app.post("/api/leaves", status_code=201)
    async def submit(request: Request):
        if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
            raise DomainError("UNSUPPORTED_MEDIA_TYPE", status=415)
        try:
            body = await request.json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise DomainError("INVALID_JSON", status=400) from None
        return await run_in_threadpool(submit_sync, parse_leave(body))

    @app.get("/api/leaves")
    def get_leaves(request: Request):
        validate_query(request, ("employee_id",))
        values = request.query_params.getlist("employee_id")
        if not values or values == [""]:
            raise DomainError("REQUIRED_FIELD", "employee_id")
        if len(values) != 1 or not re.fullmatch(r"[0-9]+", values[0]):
            raise DomainError("INVALID_VALUE", "employee_id")
        # Avoid integer overflow at the SQLite boundary, not implicit coercion.
        normalized_id = values[0].lstrip("0") or "0"
        if len(normalized_id) > 19:
            raise DomainError("EMPLOYEE_NOT_FOUND", "employee_id", 404)
        employee_id = int(normalized_id)
        if employee_id <= 0:
            raise DomainError("INVALID_VALUE", "employee_id")
        with db.connect(settings().db_path) as conn:
            return {"leaves": leave_service.get_leaves(conn, employee_id)}

    @app.api_route("/api", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
    def unknown_api(request: Request, path: str = ""):
        known = {"/api/health", "/api/employees", "/api/leaves"}
        if request.url.path in known:
            raise DomainError("METHOD_NOT_ALLOWED", status=405)
        raise DomainError("NOT_FOUND", status=404)
