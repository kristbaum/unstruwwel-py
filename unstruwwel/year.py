from datetime import datetime, timedelta
import calendar

from unstruwwel.period import Period


class Year(Period):
    def __init__(self, value):
        super().__init__()
        self.value = int(value)
        self._initialize_year()

    def _initialize_year(self):
        if self.value < 0:
            self.value = abs(self.value)
            start_date = datetime(self.value, 1, 1) - timedelta(days=1)
        else:
            start_date = datetime(self.value, 1, 1)
        self._interval = (start_date, start_date + timedelta(days=365))

    def _take_period(self, x, month):
        start_date, end_date = self._interval
        if month:
            month_days = calendar.monthrange(self.value, month)[1]
            start_date = datetime(self.value, month, 1)
            end_date = datetime(self.value, month, month_days)
        if x:
            if 1 <= x <= month_days:
                return (datetime(self.value, month, x), datetime(self.value, month, x))
        return (start_date, end_date)

    def _take_season(self, season):
        seasons = {
            "spring": (3, 5),
            "summer": (6, 8),
            "autumn": (9, 11),
            "winter": (12, 2),
        }
        return seasons.get(season)

    def _take_month(self, month_name):
        months = {v: k for k, v in enumerate(calendar.month_name)}
        return months.get(month_name.capitalize())

    def take(self, x=None, type=None, ignore_errors=False):
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
