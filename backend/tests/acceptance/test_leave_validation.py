import pytest


@pytest.mark.req("TC-08", "AC-01.1", "FR-05", "FR-08")
@pytest.mark.parametrize("field,value", [("status", "approved"), ("days", 999), ("day_units", 999)])
def test_client_cannot_supply_server_fields(client, payload, snapshot, field, value):
    before = snapshot()
    response = client.post("/api/leaves", json={**payload, field: value})
    assert response.status_code == 422
    assert response.json()["error"] == {"code": "UNKNOWN_FIELD", "message": "包含不支援的欄位", "field": field}
    assert snapshot() == before
    response = client.post("/api/leaves", json=payload)
    assert response.status_code == 201
    assert response.json()["leave"]["days"] == 1
    assert snapshot()[0][-2:] == (2, "pending")


@pytest.mark.req("TC-07", "AC-02.2", "FR-02", "FR-08")
@pytest.mark.parametrize("reason,expected", [
    ("假" * 200, "假" * 200), ("假" * 201, None),
    (" 請 假 ", "請 假"), (" \t\n", ""), (None, ""),
    ("😀", "😀"), ("e\u0301", "e\u0301"), ("👩‍💻", "👩‍💻"),
])
def test_reason_is_normalized_and_limited(client, payload, snapshot, reason, expected):
    payload["reason"] = reason
    before = snapshot()
    response = client.post("/api/leaves", json=payload)
    if expected is None:
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "REASON_TOO_LONG"
        assert response.json()["error"]["field"] == "reason"
        assert snapshot() == before
    else:
        assert response.status_code == 201
        assert response.json()["leave"]["reason"] == expected
        assert snapshot()[0][6] == expected


@pytest.mark.req("TC-07", "AC-02.2", "FR-02")
def test_reason_may_be_omitted(client, payload, snapshot):
    del payload["reason"]
    response = client.post("/api/leaves", json=payload)
    assert response.status_code == 201
    assert response.json()["leave"]["reason"] == ""
    assert snapshot()[0][6] == ""


@pytest.mark.req("TC-06", "AC-02.3", "FR-04", "FR-08")
@pytest.mark.parametrize("start,end,period,days", [
    ("2026-10-09", "2026-10-12", "full", 2),
    ("2026-10-10", "2026-10-11", "full", None),
    ("2026-10-10", "2026-10-10", "am", None),
    ("2026-10-10", "2026-10-10", "pm", None),
])
def test_weekends_do_not_count(client, payload, snapshot, start, end, period, days):
    payload.update(start_date=start, end_date=end, period=period)
    before = snapshot()
    response = client.post("/api/leaves", json=payload)
    if days is not None:
        assert response.status_code == 201
        assert response.json()["leave"]["days"] == days
        assert snapshot()[0][-2:] == (4, "pending")
    else:
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "NO_WORKDAYS"
        assert response.json()["error"]["field"] == "start_date"
        assert snapshot() == before


@pytest.mark.req("TC-05", "AC-02.3", "FR-04")
@pytest.mark.parametrize("period", ["am", "pm"])
def test_half_day_must_be_one_workday(client, payload, snapshot, period):
    payload["period"] = period
    response = client.post("/api/leaves", json=payload)
    assert response.status_code == 201
    assert response.json()["leave"]["days"] == 0.5
    assert snapshot()[0][-2:] == (1, "pending")
    before = snapshot()
    payload["end_date"] = "2026-10-13"
    response = client.post("/api/leaves", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "HALF_DAY_SINGLE_DATE"
    assert response.json()["error"]["field"] == "period"
    assert snapshot() == before


@pytest.mark.req("TC-03", "AC-02.1", "FR-01", "FR-08")
@pytest.mark.parametrize("field", ["employee_id", "leave_type", "start_date", "end_date", "period"])
def test_required_field_is_rejected_without_saving(client, payload, snapshot, field):
    del payload[field]
    before = snapshot()
    response = client.post("/api/leaves", json=payload)
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "REQUIRED_FIELD", "message": "請填寫必要欄位", "field": field}}
    assert snapshot() == before


@pytest.mark.req("TC-04", "AC-02.3", "FR-03", "FR-08")
@pytest.mark.parametrize("start,end,code,field", [
    ("2026-02-30", "2026-02-30", "INVALID_DATE", "start_date"),
    ("2026-10-13", "2026-10-12", "REVERSE_DATES", "end_date"),
])
def test_bad_dates_are_rejected(client, payload, snapshot, start, end, code, field):
    payload.update(start_date=start, end_date=end)
    before = snapshot()
    response = client.post("/api/leaves", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == code
    assert response.json()["error"]["field"] == field
    assert snapshot() == before


@pytest.mark.req("TC-03", "AC-02.1", "FR-01", "FR-08")
@pytest.mark.parametrize("field,value,status,code", [
    ("employee_id", 999, 404, "EMPLOYEE_NOT_FOUND"),
    ("employee_id", "1", 422, "INVALID_VALUE"),
    ("employee_id", True, 422, "INVALID_VALUE"),
    ("leave_type", "other", 422, "INVALID_VALUE"),
    ("period", "other", 422, "INVALID_VALUE"),
])
def test_invalid_field_is_rejected(client, payload, snapshot, field, value, status, code):
    payload[field] = value
    before = snapshot()
    response = client.post("/api/leaves", json=payload)
    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    assert response.json()["error"]["field"] == field
    assert snapshot() == before
