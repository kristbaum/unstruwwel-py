from datetime import datetime, timedelta


class Period:
    def __init__(self, *args):
        # Assuming args can include intervals, numbers, or Periods objects
        self._interval = None
        self.fuzzy = 0
        self.express = 0

        intervals = []
        fuzzy_flags = []

        for arg in args:
            if isinstance(arg, Period):
                intervals.append(arg._interval)
                fuzzy_flags.append(arg.fuzzy)
            elif isinstance(
                arg, tuple
            ):  # Assuming interval is a tuple of datetime objects
                intervals.append(arg)
            else:
                # Handle numerical scalars here
                pass

        # Combine intervals (this is a placeholder for actual logic)
        if intervals:
            self._interval = self._combine_intervals(intervals)

        # Set fuzzy flag based on input
        if fuzzy_flags:
            if any(f < 0 for f in fuzzy_flags):
                self.fuzzy = -1
            if any(f > 0 for f in fuzzy_flags):
                self.fuzzy = 1

    def _combine_intervals(self, intervals):
        # Initialize with extreme dates
        earliest_start = datetime.max
        latest_end = datetime.min

        for interval in intervals:
            start, end = interval

            # Update earliest start and latest end if necessary
            if start < earliest_start:
                earliest_start = start
            if end > latest_end:
                latest_end = end

        # Return the combined interval
        return (earliest_start, latest_end)

    def _take_period(self, x, type):
        # Placeholder for actual logic to calculate time interval
        max_value = {"quarter": 4, "third": 3, "half": 2}.get(type, 10)

        if x == "last":
            x = max_value
        if x == "first":
            x = 1

        # Ensure x is within valid range
        if not 1 <= x <= max_value:
            raise ValueError("Invalid value for x based on type")

        # Example logic to set interval (to be adapted based on R logic)
        # self._interval = some calculated interval

        # The actual logic to calculate the interval will depend on the
        # details of how intervals are represented and calculated in the R code

    @property
    def interval(self):
        if self._interval is None:
            return None

        # Standardize interval format (placeholder for actual logic)
        standardized_interval = (
            self._interval
        )  # Replace with actual standardization logic

        if self.express != 0:
            if self.express < 0:
                start_x = datetime.min
                end_x = standardized_interval[0] - timedelta(days=1)
            elif self.express > 0:
                start_x = standardized_interval[1] + timedelta(days=1)
                end_x = datetime.max

            standardized_interval = (start_x, end_x)

        return standardized_interval

    @property
    def time_span(self):
        if self._interval is None:
            return None

        start_year = self._interval[0].year
        end_year = self._interval[1].year

        # Handling extreme years, assuming -9999 and 9999 are placeholders for infinity in R
        if start_year == -9999:
            start_year = float("-inf")
        if end_year == 9999:
            end_year = float("inf")

        return sorted([start_year, end_year])

    @property
    def iso_format(self):
        if self._interval is None:
            return None

        start_date, end_date = self._interval

        # Format start and end dates in ISO 8601
        start_iso = start_date.isoformat()
        end_iso = end_date.isoformat()

        # Handling special cases for fuzzy dates and boundaries
        # This is a placeholder for the actual logic, which needs to be adapted from R
        if self.fuzzy < 0:
            start_iso += "~"
            end_iso += "~"
        elif self.fuzzy > 0:
            start_iso += "?"
            end_iso += "?"

        # Constructing the final ISO format string
        iso_string = f"{start_iso}/{end_iso}"

        return iso_string

    def set_additions(self, additions):
        if "approximate" in additions or "?" in additions:
            self.fuzzy = -1
        if "uncertain" in additions:
            self.fuzzy = 1

        if "before" in additions:
            self.express = -1
        if "after" in additions:
            self.express = 1

        return self

    def take(self, x=None, type=None, ignore_errors=False):
        try:
            if type:
                type = type.lower()
                if type in ["early", "mid", "late"]:
                    # Placeholder for handling 'early', 'mid', 'late'
                    pass
                elif type in ["quarter", "third", "half"]:
                    # Call self._take_period with appropriate arguments
                    self._take_period(x, type)
                else:
                    # Handle other types or raise an error for unsupported types
                    pass
            else:
                # Handle cases where type is None or x defines a year or decade
                pass

            # Create and return a new Periods object with adjusted interval
            return Period(
                self._interval
            )  # Assuming _interval is adjusted by this method
        except Exception as e:
            if ignore_errors:
                return self
            else:
                raise e
