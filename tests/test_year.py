from datetime import datetime
import unittest

from unstruwwel.year import Year


class TestYear(unittest.TestCase):
    """
    A test case for the Year class in the unstruwwel.year module.

    This test case contains various test methods to validate the functionality
    of the Year class for different scenarios, including invalid years, positive
    years, negative years, years with specific months, and years with specific
    months and days.
    """

    def test_invalid_year(self):
        """
        Test method to validate the behavior of the Year class when provided with
        invalid year values.

        This method tests the behavior of the Year class when provided with a future
        year, a non-integer value, and a list input. It asserts that the Year class
        raises a ValueError in each of these cases.
        """
        current_year = datetime.now().year
        if current_year < 2025:
            with self.assertRaises(ValueError):
                Year(2025)

        with self.assertRaises(ValueError):
            Year(197.5)

        with self.assertRaises(ValueError):
            Year([197, 198])

    def test_invalid_take_with_year(self):
        """
        Test method to validate the behavior of the Year class when using the `take`
        method with an invalid type parameter.

        This method tests the behavior of the Year class when the `take` method is
        called with an invalid type parameter. It asserts that the Year class raises
        a ValueError in this case.
        """
        with self.assertRaises(ValueError):
            Year(1900).take(type="j")

    def test_positive_year(self):
        """
        Test method to validate the behavior of the Year class for a positive year.

        This method tests the behavior of the Year class when provided with a positive
        year value. It asserts that the `_interval` attribute of the Year instance is
        set correctly and that the `time_span` method returns the expected year range.
        """
        self.assertEqual(
            Year(1750)._interval, (datetime(1750, 1, 1), datetime(1750, 12, 31))
        )
        self.assertEqual(Year(1750).time_span(), (1750, 1750))

    def test_positive_year_with_month(self):
        """
        Test method to validate the behavior of the Year class for a positive year with a specific month.

        This method tests the behavior of the Year class when provided with a positive
        year value and a specific month. It asserts that the `_interval` attribute of
        the Year instance is set correctly for the specified month and that the `time_span`
        method returns the expected year range.
        """
        self.assertEqual(
            Year(1750).take(type="may")._interval,
            (datetime(1750, 5, 1), datetime(1750, 5, 31)),
        )
        self.assertEqual(Year(1750).take(type="may").time_span(), (1750, 1750))

    def test_positive_year_with_month_and_day(self):
        """
        Test method to validate the behavior of the Year class for a positive year with a specific month and day.

        This method tests the behavior of the Year class when provided with a positive
        year value, a specific month, and a specific day. It asserts that the `_interval`
        attribute of the Year instance is set correctly for the specified month and day
        and that the `time_span` method returns the expected year range.
        """
        self.assertEqual(
            Year(1750).take(5, "april")._interval,
            (datetime(1750, 4, 5), datetime(1750, 4, 5)),
        )
        self.assertEqual(Year(1750).take(5, "april").time_span(), (1750, 1750))

    def test_negative_year(self):
        """
        Test method to validate the behavior of the Year class for a negative year.

        This method tests the behavior of the Year class when provided with a negative
        year value. It asserts that the `_interval` attribute of the Year instance is
        set correctly and that the `time_span` method returns the expected year range.
        """
        self.assertEqual(
            Year(-1750)._interval,
            (datetime(-1750, 1, 1), datetime(-1749, 1, 1) - timedelta(days=1))
        )
        self.assertEqual(Year(-1750).time_span(), (-1750, -1750))

    def test_negative_year_with_month(self):
        """
        Test method to validate the behavior of the Year class for a negative year with a specific month.

        This method tests the behavior of the Year class when provided with a negative
        year value and a specific month. It asserts that the `_interval` attribute of
        the Year instance is set correctly for the specified month and that the `time_span`
        method returns the expected year range.
        """
        self.assertEqual(
            Year(-1750).take(type="may")._interval,
            (datetime(-1750, 5, 1), datetime(-1750, 5, 31))
        )
        self.assertEqual(Year(-1750).take(type="may").time_span(), (-1750, -1750))

    def test_negative_year_with_month_and_day(self):
        """
        Test method to validate the behavior of the Year class for a negative year with a specific month and day.

        This method tests the behavior of the Year class when provided with a negative
        year value, a specific month, and a specific day. It asserts that the `_interval`
        attribute of the Year instance is set correctly for the specified month and day
        and that the `time_span` method returns the expected year range.
        """
        self.assertEqual(
            Year(-1750).take(5, "april")._interval,
            (datetime(-1750, 4, 5), datetime(-1750, 4, 5))
        )
        self.assertEqual(Year(-1750).take(5, "april").time_span(), (-1750, -1750))


if __name__ == "__main__":
    unittest.main()
