import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.mark.req("TC-01", "FR-01")
def test_employee_list_returns_seeded_employees_without_creating_leaves(
    tmp_path, monkeypatch
):
    # Exercise the public environment-based configuration seam, not the dev DB.
    db_path = tmp_path / "employees.sqlite3"
    monkeypatch.setenv("LEAVEBOT_DB", str(db_path))
    monkeypatch.setenv("LEAVEBOT_TODAY", "2026-10-14")

    with TestClient(create_app()) as client:
        response = client.get("/api/employees")

    assert response.status_code == 200
    assert response.json() == {
        "employees": [
            {"id": 1, "name": "員工A"},
            {"id": 2, "name": "員工B"},
            {"id": 3, "name": "員工C"},
        ]
    }
    assert db_path.is_file()
    connection = sqlite3.connect(db_path)
    try:
        assert connection.execute("SELECT COUNT(*) FROM leave_requests").fetchone()[0] == 0
    finally:
        connection.close()
