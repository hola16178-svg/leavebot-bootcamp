import pytest


@pytest.mark.req("TC-03", "FR-08")
def test_unsupported_trace_method_uses_documented_error_format(client, snapshot):
    """SDS common errors: unsupported methods use the same public JSON envelope."""
    before = snapshot()
    response = client.request("TRACE", "/api/leaves")
    assert response.status_code == 405
    assert response.json() == {
        "error": {
            "code": "METHOD_NOT_ALLOWED",
            "message": "不支援此操作方法",
            "field": None,
        }
    }
    assert snapshot() == before
