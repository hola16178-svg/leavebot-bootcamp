from datetime import date
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

EMPLOYEES = [
    {"id": 1, "name": "員工A"}, {"id": 2, "name": "員工B"},
    {"id": 3, "name": "員工C"},
]


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "leaves.sqlite3"


@pytest.fixture
def app_factory(db_path):
    def make():
        return create_app(db_path=db_path, today_provider=lambda: date(2026, 10, 14),
                          seed_employees=EMPLOYEES)
    return make


@pytest.fixture
def client(app_factory):
    with TestClient(app_factory()) as active:
        yield active


@pytest.fixture
def payload():
    return {"employee_id": 1, "leave_type": "annual", "start_date": "2026-10-12",
            "end_date": "2026-10-12", "period": "full", "reason": ""}


@pytest.fixture
def snapshot(db_path):
    def read():
        conn = sqlite3.connect(db_path)
        try:
            return conn.execute("SELECT * FROM leave_requests ORDER BY id").fetchall()
        finally:
            conn.close()
    return read
