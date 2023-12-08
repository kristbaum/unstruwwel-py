from datetime import date, timedelta

from unstruwwel.period import Period


class Century(Period):
    """
    Represents a century.

    A century is a specific period of 100 years. This class provides methods to calculate the time span
    and divide the century into early, mid, and late periods.

    Args:
        value (int or float or str): The value representing the century. It can be an integer, a float
            that represents an integer, or a string that can be converted to an integer.

    Raises:
        ValueError: If the value is not an integer or a float that represents an integer, or if the value
            is not between 1 and 21 (inclusive) or its negative counterpart.

    Attributes:
        _interval (tuple): A tuple containing the start and end dates of the century.

    Methods:
        _take_early: Returns the start and end dates of the early period of the century.
        _take_mid: Returns the start and end dates of the mid period of the century.
        _take_late: Returns the start and end dates of the late period of the century.
        time_span: Returns the start and end years of the century.

    """

    def __init__(self, value):
        super().__init__()

        if isinstance(value, str):
            value = int(value)

        # Ensure value is an integer or a float that represents an integer
        if not isinstance(value, int):
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            else:
                raise ValueError(
                    "Value must be an integer or a float that represents an integer."
                )

        if not (1 <= abs(value) < 22):
            raise ValueError(
                "Value must be between 1 and 21, inclusive, or its negative counterpart."
            )
        if value < 0:
            start_year = 1 - (abs(value + 1) * 100)
            end_year = start_year + 100
        else:
            start_year = ((value - 1) * 100) + 1
            end_year = start_year + 100

        self._interval = (
            date(start_year, 1, 1),
            date(end_year, 1, 1) - timedelta(days=1),
        )

    def _take_early(self):
        """
        Returns the start and end dates of the early period of the century.

        If the start year of the century is before year 1, the end date of the early period is calculated
        by subtracting 85 years from the start date. Otherwise, the start date of the early period is
        calculated by adding 85 years to the start date.

        Returns:
            tuple: A tuple containing the start and end dates of the early period.

        """
        start_date, end_date = self._interval
        if start_date.year < 1:
            new_end_date = start_date + timedelta(days=85 * 365.25)
        else:
            new_end_date = end_date - timedelta(days=85 * 365.25)
        return (start_date, new_end_date)

    def _take_mid(self):
        """
        Returns the start and end dates of the mid period of the century.

        The start date of the mid period is calculated by adding 45 years to the start date of the century,
        and the end date of the mid period is calculated by subtracting 45 years from the end date of the century.

        Returns:
            tuple: A tuple containing the start and end dates of the mid period.

        """
        start_date, end_date = self._interval
        new_start_date = start_date + timedelta(days=45 * 365.25)
        new_end_date = end_date - timedelta(days=45 * 365.25)
        return (new_start_date, new_end_date)

    def _take_late(self):
        """
        Returns the start and end dates of the late period of the century.

        If the start year of the century is before year 1, the start date of the late period is the same as
        the start date of the century, and the end date of the late period is calculated by subtracting
        85 years from the end date. Otherwise, the start date of the late period is calculated by adding
        85 years to the start date, and the end date of the late period is the same as the end date of the century.

        Returns:
            tuple: A tuple containing the start and end dates of the late period.

        """
        start_date, end_date = self._interval
        if start_date.year < 1:
            new_start_date = start_date
            new_end_date = end_date - timedelta(days=85 * 365.25)
        else:
            new_start_date = start_date + timedelta(days=85 * 365.25)
            new_end_date = end_date
        return (new_start_date, new_end_date)

    @property
    def time_span(self):
        """
        Returns the start and end years of the century.

        Returns:
            tuple: A tuple containing the start and end years of the century.

        """
        return (self._interval[0].year, self._interval[1].year)
