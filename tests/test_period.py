import unittest
from datetime import date

from unstruwwel.period import Period


class TestInvalidPeriod(unittest.TestCase):
    def test_invalid_period(self):
        """
        Test case for invalid period in the Period class.

        This test case checks if the Period class correctly raises an AttributeError
        when attempting to modify the interval, iso_format, or time_span attributes.

        It creates an instance of the Period class with a valid interval, and then
        attempts to modify the interval, iso_format, and time_span attributes using
        invalid values. Each modification should raise an AttributeError.

        """
        test_date = Period((date(1750, 1, 1), date(1750, 12, 31)))

        with self.assertRaises(AttributeError):
            test_date.interval = (date(1760, 1, 1), date(1760, 12, 31))

        with self.assertRaises(AttributeError):
            test_date.iso_format = "1760-01-01?/1760-12-31?"

        with self.assertRaises(AttributeError):
            test_date.time_span = (1760, 1760)


if __name__ == "__main__":
    unittest.main()
