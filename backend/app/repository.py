"""All SQL values are bound parameters; transaction ownership stays in service."""


def list_employees(conn):
    return [dict(row) for row in conn.execute("SELECT id, name FROM employees ORDER BY id")]


def employee_exists(conn, employee_id):
    if employee_id > 9223372036854775807:
        return False
    return conn.execute("SELECT 1 FROM employees WHERE id = ?", (employee_id,)).fetchone() is not None


def to_record(row):
    result = dict(row)
    result["days"] = result.pop("day_units") / 2
    return result


def insert_leave(conn, value):
    cursor = conn.execute(
        """INSERT INTO leave_requests
        (employee_id, leave_type, start_date, end_date, period, reason, day_units, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')""",
        (value["employee_id"], value["leave_type"], value["start_date"].isoformat(),
         value["end_date"].isoformat(), value["period"], value["reason"], value["day_units"]),
    )
    return to_record(conn.execute("SELECT * FROM leave_requests WHERE id = ?", (cursor.lastrowid,)).fetchone())


def list_leaves(conn, employee_id):
    return [to_record(row) for row in conn.execute(
        "SELECT * FROM leave_requests WHERE employee_id = ? ORDER BY id DESC", (employee_id,)
    )]
