import pytest


@pytest.mark.req("TC-09", "AC-03.1", "AC-03.2", "FR-09", "FR-10")
def test_lists_are_isolated_ordered_and_distinguish_unknown_employee(client, payload, snapshot):
    first = client.post("/api/leaves", json=payload).json()["leave"]
    second = client.post("/api/leaves", json={**payload, "start_date": "2026-10-13", "end_date": "2026-10-13", "period": "am"}).json()["leave"]
    other = client.post("/api/leaves", json={**payload, "employee_id": 2, "period": "pm"}).json()["leave"]
    before = snapshot()
    for employee, expected in [(1, [second, first]), (2, [other]), (3, [])]:
        response = client.get("/api/leaves", params={"employee_id": employee})
        assert response.status_code == 200
        assert response.json() == {"leaves": expected}
    response = client.get("/api/leaves", params={"employee_id": 999})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "EMPLOYEE_NOT_FOUND"
    assert snapshot() == before
