import unittest
from datetime import datetime

from unstruwwel.century import Century

class TestCentury(unittest.TestCase):
    def test_invalid_century(self):
        with self.assertRaises(ValueError):
            Century(22)
        with self.assertRaises(ValueError):
            Century(20.22)
        with self.assertRaises(ValueError):
            Century([10, 20])

    def test_positive_century(self):
        self.assertEqual(
            Century("1")._interval, (datetime(1, 1, 1), datetime(100, 12, 31))
        )
        self.assertEqual(Century("1").time_span(), (1, 100))
        self.assertEqual(
            Century(15)._interval, (datetime(1401, 1, 1), datetime(1500, 12, 31))
        )
        self.assertEqual(Century(15).time_span(), (1401, 1500))

    # Additional tests for positive century with take...

    def test_negative_century(self):
        self.assertEqual(
            Century("-1")._interval, (datetime(-100, 12, 31), datetime(-1, 1, 1))
        )
        self.assertEqual(Century("-1").time_span(), (-100, -1))
        self.assertEqual(
            Century(-15)._interval, (datetime(-1500, 12, 31), datetime(-1401, 1, 1))
        )
        self.assertEqual(Century(-15).time_span(), (-1500, -1401))

    # Additional tests for negative century with take...

    def test_invalid_take_with_errors(self):
        with self.assertRaises(ValueError):
            Century(15).take(999)
        # Additional invalid take tests...

    def test_invalid_take_without_errors(self):
        self.assertEqual(
            Century(15).take(999, ignore_errors=True)._interval,
            (datetime(1401, 1, 1), datetime(1500, 12, 31)),
        )
        # Additional invalid take tests without errors...


if __name__ == "__main__":
    unittest.main()
