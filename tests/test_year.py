from datetime import datetime
import unittest

from unstruwwel.year import Year


class TestYear(unittest.TestCase):
    def test_invalid_year(self):
        # Testing with a future year (assuming current year is earlier than 2025)
        current_year = datetime.now().year
        if current_year < 2025:
            with self.assertRaises(ValueError):
                Year(2025)

        # Testing with a non-integer value
        with self.assertRaises(ValueError):
            Year(197.5)

        # Testing with a list input
        with self.assertRaises(ValueError):
            Year([197, 198])

    def test_invalid_take_with_year(self):
        # Test for invalid type "j"
        with self.assertRaises(ValueError):
            Year(1900).take(type="j")

    def test_positive_year(self):
        # Test for the whole year 1750
        self.assertEqual(
            Year(1750)._interval, (datetime(1750, 1, 1), datetime(1750, 12, 31))
        )
        self.assertEqual(Year(1750).time_span(), (1750, 1750))

    def test_positive_year_with_month(self):
        # Test for the month of May in 1750
        self.assertEqual(
            Year(1750).take(type="may")._interval,
            (datetime(1750, 5, 1), datetime(1750, 5, 31)),
        )
        self.assertEqual(Year(1750).take(type="may").time_span(), (1750, 1750))

    def test_positive_year_with_month_and_day(self):
        # Test for April 5, 1750
        self.assertEqual(
            Year(1750).take(5, "april")._interval,
            (datetime(1750, 4, 5), datetime(1750, 4, 5)),
        )
        self.assertEqual(Year(1750).take(5, "april").time_span(), (1750, 1750))

    def test_negative_year(self):
        # Test for the whole year -1750
        self.assertEqual(
            Year(-1750)._interval,
            (datetime(-1750, 1, 1), datetime(-1749, 1, 1) - timedelta(days=1))
        )
        self.assertEqual(Year(-1750).time_span(), (-1750, -1750))

    def test_negative_year_with_month(self):
        # Test for the month of May in -1750
        self.assertEqual(
            Year(-1750).take(type="may")._interval,
            (datetime(-1750, 5, 1), datetime(-1750, 5, 31))
        )
        self.assertEqual(Year(-1750).take(type="may").time_span(), (-1750, -1750))

    def test_negative_year_with_month_and_day(self):
        # Test for April 5, -1750
        self.assertEqual(
            Year(-1750).take(5, "april")._interval,
            (datetime(-1750, 4, 5), datetime(-1750, 4, 5))
        )
        self.assertEqual(Year(-1750).take(5, "april").time_span(), (-1750, -1750))


if __name__ == "__main__":
    unittest.main()
