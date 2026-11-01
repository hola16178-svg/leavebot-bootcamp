from datetime import date
import re


def build_today_provider(value):
    if value is None:
        return date.today
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("LEAVEBOT_TODAY must be YYYY-MM-DD")
    fixed = date.fromisoformat(value)
    return lambda: fixed
