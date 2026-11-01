from . import repository
from .rules import calculate_day_units
from .errors import DomainError, SubmissionUnknown
import sqlite3


def submit_leave(conn, request):
    conn.execute("BEGIN")
    if not repository.employee_exists(conn, request["employee_id"]):
        raise DomainError("EMPLOYEE_NOT_FOUND", "employee_id", 404)
    value = dict(request)
    value["day_units"] = calculate_day_units(value["start_date"], value["end_date"], value["period"])
    record = repository.insert_leave(conn, value)
    try:
        conn.commit()
    except Exception:
        # A commit acknowledgement failure cannot safely promise no saved data.
        raise SubmissionUnknown() from None
    return record


def get_leaves(conn, employee_id):
    if not repository.employee_exists(conn, employee_id):
        raise DomainError("EMPLOYEE_NOT_FOUND", "employee_id", 404)
    return repository.list_leaves(conn, employee_id)
