"""SQLite connections and repeatable initialization."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3


@contextmanager
def connect(path):
    conn = sqlite3.connect(path, timeout=5)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    finally:
        try:
            if conn.in_transaction:
                conn.rollback()
        finally:
            conn.close()


def init_db(path, employees):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY CHECK(id > 0), name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS leave_requests (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL REFERENCES employees(id),
                leave_type TEXT NOT NULL CHECK(leave_type IN ('annual','personal','sick')),
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL CHECK(end_date >= start_date),
                period TEXT NOT NULL CHECK(period IN ('full','am','pm')),
                reason TEXT NOT NULL CHECK(length(reason) <= 200),
                day_units INTEGER NOT NULL CHECK(typeof(day_units) = 'integer' AND day_units > 0),
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status = 'pending'),
                CHECK((period = 'full' AND day_units % 2 = 0) OR
                      (period IN ('am','pm') AND day_units = 1 AND start_date = end_date))
            );
            CREATE INDEX IF NOT EXISTS leave_employee_id
                ON leave_requests(employee_id, id);
        """)
        conn.executemany(
            "INSERT INTO employees(id, name) VALUES (?, ?) ON CONFLICT(id) DO NOTHING",
            [(employee["id"], employee["name"]) for employee in employees],
        )
        conn.commit()
