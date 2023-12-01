from datetime import datetime, timedelta

from Python.accessors_period import Periods


class Decade(Periods):
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
        start_date, end_date = self._interval
        new_end_date = start_date + timedelta(days=8 * 365.25)
        return (start_date, new_end_date)

    def _take_mid(self):
        start_date, end_date = self._interval
        new_start_date = start_date + timedelta(days=4 * 365.25)
        new_end_date = end_date - timedelta(days=4 * 365.25)
        return (new_start_date, new_end_date)

    def _take_late(self):
        start_date, end_date = self._interval
        new_start_date = start_date + timedelta(days=8 * 365.25)
        return (new_start_date, end_date)
