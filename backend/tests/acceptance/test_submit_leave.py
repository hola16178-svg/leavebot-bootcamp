import pytest
from fastapi.testclient import TestClient


@pytest.mark.req("TC-10", "AC-02.4", "AC-01.4", "FR-07", "FR-08")
def test_corrected_request_and_duplicate_each_create_one_leave(client, payload, snapshot):
    bad = {**payload, "start_date": "2026-10-13"}
    response = client.post("/api/leaves", json=bad)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "REVERSE_DATES"
    assert snapshot() == []
    first = client.post("/api/leaves", json=payload)
    assert first.status_code == 201
    assert len(snapshot()) == 1
    second = client.post("/api/leaves", json=payload)
    assert second.status_code == 201
    assert second.json()["leave"]["id"] != first.json()["leave"]["id"]
    assert len(snapshot()) == 2
    assert all(row[-2:] == (2, "pending") for row in snapshot())


@pytest.mark.req("TC-02", "AC-01.1", "AC-01.2", "AC-03.1", "FR-05", "FR-09")
def test_valid_past_leave_is_saved_pending_and_survives_restart(app_factory, payload, snapshot):
    expected = {"id": 1, **payload, "days": 1, "status": "pending"}
    with TestClient(app_factory()) as client:
        response = client.post("/api/leaves", json=payload)
        assert response.status_code == 201
        assert response.json() == {"leave": expected}
        assert snapshot() == [(1, 1, "annual", "2026-10-12", "2026-10-12", "full", "", 2, "pending")]
    with TestClient(app_factory()) as client:
        response = client.get("/api/leaves", params={"employee_id": 1})
        assert response.status_code == 200
        assert response.json() == {"leaves": [expected]}
        assert len(snapshot()) == 1
