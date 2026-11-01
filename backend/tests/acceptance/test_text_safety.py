import sqlite3

import pytest


@pytest.mark.req("TC-12", "FR-02", "NFR-01", "AC-03.1")
@pytest.mark.parametrize("reason", ["<b>請假</b>", "'); DROP TABLE employees; --"])
def test_user_text_is_stored_as_text(client, payload, snapshot, db_path, reason):
    existing = client.post("/api/leaves", json={**payload, "employee_id": 2}).json()["leave"]
    response = client.post("/api/leaves", json={**payload, "reason": reason})
    assert response.status_code == 201
    assert response.json()["leave"]["reason"] == reason
    assert client.get("/api/leaves?employee_id=1").json()["leaves"][0]["reason"] == reason
    assert client.get("/api/leaves?employee_id=2").json() == {"leaves": [existing]}
    assert client.get("/api/employees").json() == {"employees": [
        {"id": 1, "name": "員工A"}, {"id": 2, "name": "員工B"}, {"id": 3, "name": "員工C"},
    ]}
    assert len(snapshot()) == 2
