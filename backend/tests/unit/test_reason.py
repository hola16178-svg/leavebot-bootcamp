import pytest

from app.rules import normalize_reason


@pytest.mark.req("TC-07", "AC-02.2", "FR-02")
@pytest.mark.parametrize("value,expected,count", [
    (" 請 假 ", "請 假", 3), (" \t\n", "", 0),
    ("😀", "😀", 1), ("e\u0301", "e\u0301", 2), ("👩‍💻", "👩‍💻", 3),
])
def test_worked_codepoint_examples(value, expected, count):
    actual = normalize_reason(value)
    assert actual == expected
    assert len(actual) == count
