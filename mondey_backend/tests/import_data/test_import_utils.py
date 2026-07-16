import pytest

from mondey_backend.import_data.utils import parse_weeks


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("34", (34, 0)),
        ("28+6", (28, 6)),
        ("36,6", (36, 6)),
        ("34 +3", (34, 3)),
        ("37. Woche", (37, 0)),
        ("36.0", (36, 0)),
        ("35+6 SSW", (35, 6)),
        ("36.+3", (36, 3)),
        ("36SSW ( Eineiige Zwillinge )", (36, 0)),
        (None, (0, 0)),
        ("<null>", (0, 0)),
        ("unknown", (0, 0)),
    ],
)
def test_parse_weeks(value, expected):
    assert parse_weeks(value) == expected
