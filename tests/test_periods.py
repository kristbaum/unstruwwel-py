import pytest
from dataclasses import FrozenInstanceError

from unstruwwel_py.periods import Periods


def test_invalid_period():
    x = Periods(("1750-01-01", "1750-12-31"))

    with pytest.raises(FrozenInstanceError):
        x.interval = ("1760-01-01", "1760-12-31")
    with pytest.raises(FrozenInstanceError):
        x.iso_format = "1760-01-01?/1760-12-31?"
    with pytest.raises(FrozenInstanceError):
        x.time_span = (1760, 1760)
