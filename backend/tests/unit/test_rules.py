from datetime import date

import pytest

from app.rules import calculate_day_units
from app.errors import DomainError


@pytest.mark.req("TC-05", "TC-06", "AC-02.3", "FR-04")
@pytest.mark.parametrize("start,end,period,units", [
    (date(2026, 10, 9), date(2026, 10, 12), "full", 4),
    (date(2026, 10, 12), date(2026, 10, 12), "am", 1),
    (date(2026, 10, 12), date(2026, 10, 12), "pm", 1),
])
def test_worked_day_examples(start, end, period, units):
    assert calculate_day_units(start, end, period) == units


@pytest.mark.req("TC-05", "TC-06", "AC-02.3", "FR-04")
@pytest.mark.parametrize("start,end,period,code", [
    (date(2026, 10, 12), date(2026, 10, 13), "am", "HALF_DAY_SINGLE_DATE"),
    (date(2026, 10, 10), date(2026, 10, 11), "full", "NO_WORKDAYS"),
    (date(2026, 10, 10), date(2026, 10, 10), "pm", "NO_WORKDAYS"),
])
def test_worked_invalid_day_examples(start, end, period, code):
    with pytest.raises(DomainError) as caught:
        calculate_day_units(start, end, period)
    assert caught.value.code == code
