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

    def test_positive_century_with_take(self):
        # First half of the 15th century
        self.assertEqual(
            Century(15).take(1, "half")._interval,
            (datetime(1401, 1, 1), datetime(1450, 12, 31)),
        )

        # Second quarter of the 15th century
        self.assertEqual(
            Century(15).take(2, "quarter")._interval,
            (datetime(1426, 1, 1), datetime(1450, 12, 31)),
        )

        # Last third of the 15th century
        self.assertEqual(
            Century(15).take("last", "third")._interval,
            (datetime(1467, 1, 1), datetime(1500, 12, 31)),
        )

        # Early part of the 15th century
        self.assertEqual(
            Century(15).take(type="early")._interval,
            (datetime(1401, 1, 1), datetime(1415, 12, 31)),
        )

        # Late part of the 15th century
        self.assertEqual(
            Century(15).take(type="late")._interval,
            (datetime(1486, 1, 1), datetime(1500, 12, 31)),
        )

        # Middle of the 15th century
        self.assertEqual(
            Century(15).take(type="mid")._interval,
            (datetime(1446, 1, 1), datetime(1455, 12, 31)),
        )

        # Third decade of the 15th century
        self.assertEqual(
            Century(15).take(3)._interval,
            (datetime(1421, 1, 1), datetime(1430, 12, 31)),
        )

        # Last half of the 15th century
        self.assertEqual(
            Century(15).take("last", "half")._interval,
            (datetime(1451, 1, 1), datetime(1500, 12, 31)),
        )

    def test_negative_century(self):
        # Test for the 1st century BC
        self.assertEqual(
            Century("-1")._interval, (datetime(-100, 12, 31), datetime(-1, 1, 1))
        )
        self.assertEqual(Century("-1").time_span(), (-100, -1))

        # Test for the 15th century BC
        self.assertEqual(
            Century(-15)._interval, (datetime(-1500, 12, 31), datetime(-1401, 1, 1))
        )
        self.assertEqual(Century(-15).time_span(), (-1500, -1401))

    def test_negative_century_with_take(self):
        # First half of the 15th century BC
        self.assertEqual(
            Century(-15).take(1, "half")._interval,
            (datetime(-1450, 12, 31), datetime(-1401, 1, 1)),
        )

        # Second quarter of the 15th century BC
        self.assertEqual(
            Century(-15).take(2, "quarter")._interval,
            (datetime(-1450, 12, 31), datetime(-1426, 1, 1)),
        )

        # Last third of the 15th century BC
        self.assertEqual(
            Century(-15).take("last", "third")._interval,
            (datetime(-1500, 12, 31), datetime(-1467, 1, 1)),
        )

        # Early part of the 15th century BC
        self.assertEqual(
            Century(-15).take(type="early")._interval,
            (datetime(-1415, 12, 31), datetime(-1401, 1, 1)),
        )

        # Late part of the 15th century BC
        self.assertEqual(
            Century(-15).take(type="late")._interval,
            (datetime(-1500, 12, 31), datetime(-1486, 1, 1)),
        )

        # Middle of the 15th century BC
        self.assertEqual(
            Century(-15).take(type="mid")._interval,
            (datetime(-1455, 12, 31), datetime(-1446, 1, 1)),
        )

        # Third decade of the 15th century BC
        self.assertEqual(
            Century(-15).take(3)._interval,
            (datetime(-1430, 12, 31), datetime(-1421, 1, 1)),
        )

    def test_invalid_take_with_errors(self):
        century = Century(15)

        with self.assertRaises(ValueError):
            century.take(999)

        with self.assertRaises(ValueError):
            century.take(type="abc")

        with self.assertRaises(ValueError):
            century.take(3, type="half")

        with self.assertRaises(ValueError):
            century.take(4, type="third")

        with self.assertRaises(ValueError):
            century.take(5, type="quarter")

    def test_invalid_take_without_errors(self):
        century = Century(15)
        expected_interval = (datetime(1401, 1, 1), datetime(1500, 12, 31))

        self.assertEqual(
            century.take(999, ignore_errors=True)._interval, expected_interval
        )
        self.assertEqual(
            century.take(3, "half", ignore_errors=True)._interval, expected_interval
        )
        self.assertEqual(
            century.take(4, "third", ignore_errors=True)._interval, expected_interval
        )
        self.assertEqual(
            century.take(5, "quarter", ignore_errors=True)._interval, expected_interval
        )
        self.assertEqual(
            century.take(type="abc", ignore_errors=True)._interval, expected_interval
        )


if __name__ == "__main__":
    unittest.main()
