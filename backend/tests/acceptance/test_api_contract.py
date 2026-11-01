import pytest


@pytest.mark.req("TC-03", "FR-01", "FR-08")
@pytest.mark.parametrize("path,code,field", [
    ("/api/leaves", "REQUIRED_FIELD", "employee_id"),
    ("/api/leaves?employee_id=1&employee_id=2", "INVALID_VALUE", "employee_id"),
    ("/api/leaves?employee_id=-1", "INVALID_VALUE", "employee_id"),
    ("/api/employees?extra=1", "UNKNOWN_FIELD", "extra"),
])
def test_query_errors_follow_contract(client, snapshot, path, code, field):
    before = snapshot()
    response = client.get(path)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == code
    assert response.json()["error"]["field"] == field
    assert snapshot() == before


@pytest.mark.req("TC-03", "FR-08")
@pytest.mark.parametrize("body,content_type,status,code", [
    ("{", "application/json", 400, "INVALID_JSON"),
    ("{}", "text/plain", 415, "UNSUPPORTED_MEDIA_TYPE"),
    ("[]", "application/json", 422, "INVALID_VALUE"),
])
def test_body_errors_follow_contract(client, snapshot, body, content_type, status, code):
    before = snapshot()
    response = client.post("/api/leaves", content=body, headers={"content-type": content_type})
    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    assert snapshot() == before
