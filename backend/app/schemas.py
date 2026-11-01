"""Ordered input parsing; expected errors use the public error contract."""
from datetime import date
import re

from .errors import DomainError
from .rules import normalize_reason

REQUIRED = ("employee_id", "leave_type", "start_date", "end_date", "period")


def parse_leave(body):
    if not isinstance(body, dict):
        raise DomainError("INVALID_VALUE")
    unknown = sorted(set(body) - set(REQUIRED) - {"reason"})
    if unknown:
        raise DomainError("UNKNOWN_FIELD", unknown[0])
    result = dict(body)
    for field in REQUIRED:
        if field not in body or body[field] is None or body[field] == "":
            raise DomainError("REQUIRED_FIELD", field)
        value = body[field]
        if field == "employee_id":
            if type(value) is not int or value <= 0:
                raise DomainError("INVALID_VALUE", field)
        elif type(value) is not str:
            raise DomainError("INVALID_VALUE", field)
        elif field == "leave_type" and value not in ("annual", "personal", "sick"):
            raise DomainError("INVALID_VALUE", field)
        elif field == "period" and value not in ("full", "am", "pm"):
            raise DomainError("INVALID_VALUE", field)
        if field in ("start_date", "end_date"):
            try:
                if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
                    raise ValueError
                result[field] = date.fromisoformat(value)
            except ValueError:
                raise DomainError("INVALID_DATE", field) from None
    result["reason"] = normalize_reason(body.get("reason"))
    return result
