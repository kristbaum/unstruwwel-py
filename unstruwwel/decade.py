from datetime import datetime, timedelta
from period import Period


class Decade(Period):
    """
    Represents a decade period.

    Args:
        value (int): The starting year of the decade. If negative, it represents the ending year of the decade.
        official_def (bool, optional): Specifies whether the decade follows the official definition. Defaults to False.

    Attributes:
        _interval (tuple): A tuple containing the start and end dates of the decade period.

    Methods:
        _take_early(): Returns a tuple with the start and new end dates for the early part of the decade.
        _take_mid(): Returns a tuple with the new start and end dates for the middle part of the decade.
        _take_late(): Returns a tuple with the new start and end dates for the late part of the decade.
    """

    def __init__(self, value, official_def=False):
        super().__init__()
        value = int(value)
        if value < 0:
            start_year = abs(value)
            if official_def:
                start_year -= 1
            end_year = start_year + 10
        else:
            start_year = value
            if official_def:
                start_year += 1
            end_year = start_year + 10

        self._interval = (
            datetime(start_year, 1, 1),
            datetime(end_year, 1, 1) - timedelta(days=1),
        )

    def _take_early(self):
        """
        Returns the start and new end dates for the early part of the decade.

        Returns:
            tuple: A tuple containing the start and new end dates.
        """
        start_date, end_date = self._interval
        new_end_date = start_date + timedelta(days=8 * 365.25)
        return (start_date, new_end_date)

    def _take_mid(self):
        """
        Returns the new start and end dates for the middle part of the decade.

        Returns:
            tuple: A tuple containing the new start and end dates.
        """
        start_date, end_date = self._interval
        new_start_date = start_date + timedelta(days=4 * 365.25)
        new_end_date = end_date - timedelta(days=4 * 365.25)
        return (new_start_date, new_end_date)

    def _take_late(self):
        """
        Returns the new start and end dates for the late part of the decade.

        Returns:
            tuple: A tuple containing the new start and end dates.
        """
        start_date, end_date = self._interval
        new_start_date = start_date + timedelta(days=8 * 365.25)
        return (new_start_date, end_date)
