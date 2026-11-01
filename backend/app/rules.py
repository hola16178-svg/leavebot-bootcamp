from datetime import timedelta
from .errors import DomainError

WHITE_SPACE = "\u0009\u000a\u000b\u000c\u000d\u0020\u0085\u00a0\u1680" + "".join(
    chr(code) for code in range(0x2000, 0x200B)
) + "\u2028\u2029\u202f\u205f\u3000"


def normalize_reason(value):
    if value is not None and type(value) is not str:
        raise DomainError("INVALID_VALUE", "reason")
    result = (value or "").strip(WHITE_SPACE)
    if len(result) > 200:
        raise DomainError("REASON_TOO_LONG", "reason")
    return result


def calculate_day_units(start, end, period):
    if end < start:
        raise DomainError("REVERSE_DATES", "end_date")
    if period != "full" and start != end:
        raise DomainError("HALF_DAY_SINGLE_DATE", "period")
    length = (end - start).days + 1
    weeks, remainder = divmod(length, 7)
    workdays = weeks * 5 + sum(
        (start + timedelta(days=offset)).weekday() < 5 for offset in range(remainder)
    )
    if workdays == 0:
        raise DomainError("NO_WORKDAYS", "start_date")
    return workdays * 2 if period == "full" else 1
