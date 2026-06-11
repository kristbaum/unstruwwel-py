import pytest

from unstruwwel import Periods
from unstruwwel.dates import Date, Interval


def test_read_only_properties():
    x = Periods(interval=Interval(Date(1750, 1, 1), Date(1750, 12, 31)))

    with pytest.raises(AttributeError):
        x.interval = Interval(Date(1760, 1, 1), Date(1760, 12, 31))
    with pytest.raises(AttributeError):
        x.iso_format = "1760-01-01?/1760-12-31?"
    with pytest.raises(AttributeError):
        x.time_span = (1760, 1760)


def test_combines_parts_into_spanning_interval():
    span = Periods(parts=["1752", "1760"])
    assert span.time_span == (1752, 1760)
