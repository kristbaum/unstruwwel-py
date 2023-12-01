import unittest
from datetime import datetime

from unstruwwel.period import Period


class TestInvalidPeriod(unittest.TestCase):
    def test_invalid_period(self):
        x = Period((datetime(1750, 1, 1), datetime(1750, 12, 31)))

        with self.assertRaises(AttributeError):
            x.interval = (datetime(1760, 1, 1), datetime(1760, 12, 31))

        with self.assertRaises(AttributeError):
            x.iso_format = "1760-01-01?/1760-12-31?"

        with self.assertRaises(AttributeError):
            x.time_span = (1760, 1760)


if __name__ == "__main__":
    unittest.main()
