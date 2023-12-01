from datetime import datetime, timedelta

from unstruwwel.period import Periods


class Century(Periods):
    def __init__(self, value):
        super().__init__()
        value = int(value)
        if value < 0:
            start_year = 1 - (abs(value + 1) * 100)
            end_year = start_year + 100
        else:
            start_year = (value - 1) * 100
            end_year = start_year + 100

        self._interval = (
            datetime(start_year, 1, 1),
            datetime(end_year, 1, 1) - timedelta(days=1),
        )

    def _take_early(self):
        start_date, end_date = self._interval
        if start_date.year < 1:
            new_end_date = start_date + timedelta(days=85 * 365.25)
        else:
            new_end_date = end_date - timedelta(days=85 * 365.25)
        return (start_date, new_end_date)

    def _take_mid(self):
        start_date, end_date = self._interval
        new_start_date = start_date + timedelta(days=45 * 365.25)
        new_end_date = end_date - timedelta(days=45 * 365.25)
        return (new_start_date, new_end_date)

    def _take_late(self):
        start_date, end_date = self._interval
        if start_date.year < 1:
            new_start_date = start_date
            new_end_date = end_date - timedelta(days=85 * 365.25)
        else:
            new_start_date = start_date + timedelta(days=85 * 365.25)
            new_end_date = end_date
        return (new_start_date, new_end_date)

    def time_span(self):
        return (self._interval[0].year, self._interval[1].year)
