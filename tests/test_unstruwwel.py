import unittest

from unstruwwel.unstruwwel import unstruwwel


class TestUnstruwwel(unittest.TestCase):
    """
    A test case class for the unstruwwel module.

    This class contains test methods to verify the functionality of the unstruwwel module.
    """

    def test_no_language(self):
        """
        Test to ensure an error is raised when no language is provided.
        """
        with self.assertRaises(Exception):
            unstruwwel("1460", scheme="object")

    def test_no_date(self):
        """
        Test for handling 'undatiert' and None with a specified language.
        """
        self.assertEqual(unstruwwel("undatiert", "de"), (None, None))
        self.assertEqual(unstruwwel(None, "de"), (None, None))

    def test_approximate_date(self):
        """
        Test for handling an approximate date.
        """
        result = unstruwwel("1460?", "en", scheme="object")
        self.assertEqual(result.fuzzy, -1)
        self.assertEqual(result.time_span, (1460, 1460))
        self.assertEqual(result.iso_format, "1460-01-01~/1460-12-31~")

    def test_uncertain_date(self):
        """
        Test for handling an uncertain date.
        """
        result = unstruwwel("etwa 1842", "de", scheme="object")
        self.assertEqual(result.fuzzy, 1)
        self.assertEqual(result.time_span, (1842, 1842))
        self.assertEqual(result.iso_format, "1842-01-01?/1842-12-31?")

    def test_date_with_year(self):
        """
        Test for handling a date with only the year.
        """
        self.assertEqual(unstruwwel("1842", "en"), (1842, 1842))

    def test_date_with_multiple_years(self):
        """
        Test for handling a date with multiple years.
        """
        result = unstruwwel("(Guss vor 1906) 1897", "de", scheme="object")
        self.assertEqual(result[0].time_span, (-float("inf"), 1905))
        self.assertEqual(result[1].time_span, (1897, 1897))
        self.assertEqual(result[0].iso_format, "..1905-12-31")
        self.assertEqual(result[1].iso_format, "1897-01-01/1897-12-31")

    def test_date_with_year_interval(self):
        """
        Test for handling a date with a year interval.
        """
        self.assertEqual(unstruwwel("1752/60", "en"), (1752, 1760))

    def test_date_with_year_and_season(self):
        """
        Test for handling a date with year and season.
        """
        result_autumn = unstruwwel("Autumn 1945", "en", scheme="object")
        self.assertEqual(result_autumn.time_span, (1945, 1945))
        self.assertEqual(result_autumn.iso_format, "1945-09-01/1945-11-30")

        result_before_summer = unstruwwel("vor dem Sommer 1907", "de", scheme="object")
        self.assertEqual(result_before_summer.time_span, (-float("inf"), 1907))
        self.assertEqual(result_before_summer.iso_format, "..1907-05-31")

    def test_date_with_year_and_month(self):
        """
        Test for handling a date with year and month.
        """
        result_may = unstruwwel("May 1901", "en", scheme="object")
        self.assertEqual(result_may.time_span, (1901, 1901))
        self.assertEqual(result_may.iso_format, "1901-05-01/1901-05-31")

        result_after_june = unstruwwel("after June 1860", "en", scheme="object")
        self.assertEqual(result_after_june.time_span, (1860, float("inf")))
        self.assertEqual(result_after_june.iso_format, "1860-07-01..")

    def test_date_with_year_month_and_day(self):
        """
        Test for handling a date with year, month, and day.
        """
        result_jan_1 = unstruwwel("January 1, 1856", "en", scheme="object")
        self.assertEqual(result_jan_1.time_span, (1856, 1856))
        self.assertEqual(result_jan_1.iso_format, "1856-01-01/1856-01-01")

    def test_date_with_multiple_years_months_days(self):
        """
        Test for handling a date with multiple years, months, and days.
        """
        result_july = unstruwwel("13. Juli 1882 - 15. Juli 1882", "de", scheme="object")
        self.assertEqual(result_july[0].time_span, (1882, 1882))
        self.assertEqual(result_july[1].time_span, (1882, 1882))
        self.assertEqual(result_july[0].iso_format, "1882-07-13/1882-07-13")
        self.assertEqual(result_july[1].iso_format, "1882-07-15/1882-07-15")

    def test_date_with_decade(self):
        """
        Test for handling a date with a decade.
        """
        self.assertEqual(unstruwwel("1840s", "en"), (1840, 1849))
        self.assertEqual(unstruwwel("1760er Jahre", "de"), (1760, 1769))

    def test_date_with_uncertain_decade(self):
        """
        Test for handling a date with an uncertain decade.
        """
        result = unstruwwel("etwa 1550er Jahre", "de", scheme="object")
        self.assertEqual(result.fuzzy, 1)
        self.assertEqual(result.time_span, (1550, 1559))
        self.assertEqual(result.iso_format, "1550-01-01?/1559-12-31?")

    def test_date_with_century(self):
        """
        Test for handling a date with a century.
        """
        result_5th_cent = unstruwwel("1st half 5th century", "en", scheme="object")
        self.assertEqual(result_5th_cent.time_span, (401, 450))
        self.assertEqual(result_5th_cent.iso_format, "0401-01-01/0450-12-31")

        self.assertEqual(unstruwwel("19. Jh.", "de"), (1801, 1900))
        self.assertEqual(unstruwwel("5. Jh. v. Chr", "de"), (-500, -401))

        result_last_third_17th = unstruwwel("last third 17th cent", "en")
        self.assertEqual(result_last_third_17th, (1667, 1700))

    def test_date_with_uncertain_century(self):
        """
        Test for handling a date with an uncertain century.
        """
        result_18th_cent = unstruwwel("circa 18th century", "en", scheme="object")
        self.assertEqual(result_18th_cent.fuzzy, -1)
        self.assertEqual(result_18th_cent.time_span, (1701, 1800))
        self.assertEqual(result_18th_cent.iso_format, "1701-01-01~/1800-12-31~")

    def test_trailing_zero(self):
        """
        Test for handling a date with a trailing zero.
        """
        result_2nd_cent = unstruwwel("ca. 1. Hälfte 2. Jh.", "de", scheme="object")
        self.assertEqual(result_2nd_cent.time_span, (101, 150))
        self.assertEqual(result_2nd_cent.iso_format, "0101-01-01~/0150-12-31~")

        result_2nd_cent_bc = unstruwwel("ca. 2. Jh. v. Chr", "de", scheme="object")
        self.assertEqual(result_2nd_cent_bc.time_span, (-200, -101))
        self.assertEqual(result_2nd_cent_bc.iso_format, "-0200-12-31~/-0101-01-01~")

    def test_duplicate_dates(self):
        """
        Test for handling duplicate dates.
        """
        dates = unstruwwel(["late 16th century", "ca. 1920"] * 10, "en")
        self.assertTrue(dates[0] == dates[2])
        self.assertTrue(dates[1] == dates[3])

    def test_midas_date_with_negative_year(self):
        """
        Test for handling a MIDAS date with a negative year.
        """
        self.assertEqual(unstruwwel("2100ante/1550ante", "de"), (-2100, -1550))
