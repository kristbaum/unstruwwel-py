from datetime import date, timedelta
import calendar
from unstruwwel.period import Period


class Year(Period):
    """
    Represents a specific year.

    Args:
        value (int): The value of the year.

    Attributes:
        value (int): The value of the year.
        _interval (tuple): The start and end dates of the year.

    Methods:
        _initialize_year: Initializes the year and sets the start and end dates.
        _take_period: Takes a specific period within the year.
        _take_season: Takes a specific season within the year.
        _take_month: Takes a specific month within the year.
        take: Takes a specific period, season, or month within the year.

    Inherits:
        Period: A base class representing a time period.
    """

    def __init__(self, value):
        super().__init__()
        self.value = int(value)
        self._initialize_year()

    def _initialize_year(self):
        """
        Initializes the year and sets the start and end dates.
        If the year is negative, the start date is set to the previous year's December 31st.
        Otherwise, the start date is set to January 1st of the year.
        """
        if self.value < 0:
            self.value = abs(self.value)
            start_date = date(self.value, 1, 1) - timedelta(days=1)
        else:
            start_date = date(self.value, 1, 1)
        self._interval = (start_date, start_date + timedelta(days=365))

    def _take_period(self, x, month):
        """
        Takes a specific period within the year.

        Args:
            x (int): The day of the month.
            month (int): The month.

        Returns:
            tuple: The start and end dates of the period.
        """
        start_date, end_date = self._interval
        if month:
            month_days = calendar.monthrange(self.value, month)[1]
            start_date = date(self.value, month, 1)
            end_date = date(self.value, month, month_days)
        if x:
            if 1 <= x <= month_days:
                return (date(self.value, month, x), date(self.value, month, x))
        return (start_date, end_date)

    def _take_season(self, season):
        """
        Takes a specific season within the year.

        Args:
            season (str): The season.

        Returns:
            tuple: The start and end months of the season.
        """
        seasons = {
            "spring": (3, 5),
            "summer": (6, 8),
            "autumn": (9, 11),
            "winter": (12, 2),
        }
        return seasons.get(season)

    def _take_month(self, month_name):
        """
        Takes a specific month within the year.

        Args:
            month_name (str): The name of the month.

        Returns:
            int: The month number.
        """
        months = {v: k for k, v in enumerate(calendar.month_name)}
        return months.get(month_name.capitalize())

    def take(self, x=None, type=None, ignore_errors=False):
        """
        Takes a specific period, season, or month within the year.

        Args:
            x (int, optional): The day of the month. Defaults to None.
            type (str, optional): The type of period, season, or month. Defaults to None.
            ignore_errors (bool, optional): Whether to ignore errors. Defaults to False.

        Returns:
            list or tuple: The start and end dates of the period, season, or month.
        """
        try:
            if type:
                if type.lower() in ["spring", "summer", "autumn", "winter"]:
                    months = self._take_season(type.lower())
                    return [
                        self._take_period(None, month)
                        for month in range(months[0], months[1] + 1)
                    ]
                else:
                    month = self._take_month(type)
                    if month:
                        return self._take_period(x, month)
            return self._interval
        except Exception as e:
            if ignore_errors:
                return self
            else:
                raise e
