from fastapi.testclient import TestClient

from app.main import create_app
from datetime import date


def test_health_returns_service_status(tmp_path):
    # Ticket 000 skeleton check; employee-list coverage of TC-01 is ticket 001.
    with TestClient(create_app(db_path=tmp_path / "health.sqlite3",
                              today_provider=lambda: date(2026, 10, 14))) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
