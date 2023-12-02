from datetime import datetime, timedelta
import unittest

from unstruwwel.decade import Decade


class TestDecade(unittest.TestCase):
    def test_invalid_decade(self):
        with self.assertRaises(ValueError):
            Decade(203)
        with self.assertRaises(ValueError):
            Decade(2021)
        with self.assertRaises(ValueError):
            Decade(197.5)
        with self.assertRaises(ValueError):
            Decade([197, 198])

    def test_positive_decade(self):
        # Test for the decade starting in 1770
        self.assertEqual(
            Decade(1770)._interval,
            (datetime(1770, 1, 1), datetime(1780, 1, 1) - timedelta(days=1)),
        )
        self.assertEqual(Decade(1770).time_span(), (1770, 1779))

        # Test for the decade starting in 1950 with the official definition
        self.assertEqual(
            Decade(1950, official_def=True)._interval,
            (datetime(1951, 1, 1), datetime(1961, 1, 1) - timedelta(days=1)),
        )
        self.assertEqual(Decade(1950, official_def=True).time_span(), (1951, 1960))

    def test_positive_decade_with_take(self):
        # First half of the 1970s
        self.assertEqual(
            Decade(1970).take(1, "half")._interval,
            (datetime(1970, 1, 1), datetime(1975, 1, 1) - timedelta(days=1)),
        )

        # Early part of the 1970s
        self.assertEqual(
            Decade(1970).take(type="early")._interval,
            (datetime(1970, 1, 1), datetime(1972, 1, 1) - timedelta(days=1)),
        )

        # Late part of the 1970s
        self.assertEqual(
            Decade(1970).take(type="late")._interval,
            (datetime(1978, 1, 1), datetime(1980, 1, 1) - timedelta(days=1)),
        )

        # Middle of the 1970s
        self.assertEqual(
            Decade(1970).take(type="mid")._interval,
            (datetime(1974, 1, 1), datetime(1976, 1, 1) - timedelta(days=1)),
        )

        # Third year of the 1970s
        self.assertEqual(
            Decade(1970).take(3)._interval,
            (datetime(1972, 1, 1), datetime(1973, 1, 1) - timedelta(days=1)),
        )

    def test_negative_decade(self):
        # Decade starting in 1770 BC
        self.assertEqual(
            Decade(-1770)._interval, (datetime(-1779, 12, 31), datetime(-1770, 1, 1))
        )
        self.assertEqual(Decade(-1770).time_span(), (-1779, -1770))

        # Decade starting in 1950 BC with the official definition
        self.assertEqual(
            Decade(-1950, official_def=True)._interval,
            (datetime(-1960, 12, 31), datetime(-1951, 1, 1)),
        )
        self.assertEqual(Decade(-1950, official_def=True).time_span(), (-1960, -1951))

    def test_negative_decade_with_take(self):
        # First half of the 1970s BC
        self.assertEqual(
            Decade(-1970).take(1, "half")._interval,
            (datetime(-1974, 12, 31), datetime(-1970, 1, 1)),
        )

        # Early part of the 1970s BC
        self.assertEqual(
            Decade(-1970).take(type="early")._interval,
            (datetime(-1971, 12, 31), datetime(-1970, 1, 1)),
        )

        # Late part of the 1970s BC
        self.assertEqual(
            Decade(-1970).take(type="late")._interval,
            (datetime(-1979, 12, 31), datetime(-1978, 1, 1)),
        )

        # Middle of the 1970s BC
        self.assertEqual(
            Decade(-1970).take(type="mid")._interval,
            (datetime(-1975, 12, 31), datetime(-1974, 1, 1)),
        )

        # Third year of the 1970s BC
        self.assertEqual(
            Decade(-1970).take(3)._interval,
            (datetime(-1972, 1, 1), datetime(-1971, 12, 31)),
        )

    def test_invalid_take_with_errors(self):
        decade = Decade(1970)

        with self.assertRaises(ValueError):
            decade.take(99)

        with self.assertRaises(ValueError):
            decade.take(type="abc")

        with self.assertRaises(ValueError):
            decade.take(3, "half")

        with self.assertRaises(ValueError):
            decade.take(4, "third")

        with self.assertRaises(ValueError):
            decade.take(5, "quarter")

    def test_invalid_take_without_errors(self):
        expected_interval = (
            datetime(1970, 1, 1),
            datetime(1980, 1, 1) - timedelta(days=1),
        )
        decade = Decade(1970)

        self.assertEqual(
            decade.take(99, ignore_errors=True)._interval, expected_interval
        )
        self.assertEqual(
            decade.take(3, "half", ignore_errors=True)._interval, expected_interval
        )
        self.assertEqual(
            decade.take(4, "third", ignore_errors=True)._interval, expected_interval
        )
        self.assertEqual(
            decade.take(5, "quarter", ignore_errors=True)._interval, expected_interval
        )
        self.assertEqual(
            decade.take(type="abc", ignore_errors=True)._interval, expected_interval
        )


if __name__ == "__main__":
    unittest.main()
