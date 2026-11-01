import sqlite3

import pytest

from app import repository, db


@pytest.mark.req("TC-11", "FR-05", "FR-08", "NFR-02")
def test_write_failure_rolls_back_insert(client, payload, snapshot, monkeypatch):
    before = snapshot()
    real_insert = repository.insert_leave
    def fail_after_insert(conn, value):
        real_insert(conn, value)
        raise sqlite3.OperationalError("write failure before commit")
    monkeypatch.setattr(repository, "insert_leave", fail_after_insert)
    response = client.post("/api/leaves", json=payload)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DB_UNAVAILABLE"
    assert snapshot() == before


@pytest.mark.req("TC-11", "FR-05", "NFR-02")
def test_uncertain_commit_does_not_claim_no_data(client, payload, snapshot, monkeypatch):
    real_connect = sqlite3.connect
    class UncertainConnection(sqlite3.Connection):
        def commit(self):
            super().commit()
            raise sqlite3.OperationalError("commit acknowledgement lost")
    def connect_with_uncertain_commit(*args, **kwargs):
        return real_connect(*args, **kwargs, factory=UncertainConnection)
    monkeypatch.setattr(db.sqlite3, "connect", connect_with_uncertain_commit)
    response = client.post("/api/leaves", json=payload)
    assert response.status_code == 503
    assert response.json() == {"error": {"code": "SUBMISSION_UNKNOWN", "message": "無法確認是否送出成功，請先查看我的假單，再決定是否重送", "field": None}}
    # This controlled scenario really committed; it must not be called a rejection.
    assert len(snapshot()) == 1


@pytest.mark.req("TC-11", "FR-08", "NFR-02")
def test_database_read_failure_is_not_an_empty_list(client, snapshot, monkeypatch):
    before = snapshot()
    def fail_read(conn, employee_id):
        raise sqlite3.OperationalError("private SQL path and reason")
    monkeypatch.setattr(repository, "list_leaves", fail_read)
    response = client.get("/api/leaves", params={"employee_id": 1})
    assert response.status_code == 503
    assert response.json() == {"error": {"code": "DB_UNAVAILABLE", "message": "資料庫暫時無法使用，請稍後再試", "field": None}}
    assert snapshot() == before
