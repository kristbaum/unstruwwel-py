from datetime import date, timedelta


class Period:
    """
    Represents a time period with start and end dates.

    Args:
        *args: Variable length arguments that can include intervals, numbers, or Period objects.

    Attributes:
        _interval (tuple): The combined interval of the time period.
        fuzzy (int): The fuzzy flag indicating the level of uncertainty (-1 for approximate, 0 for exact, 1 for uncertain).
        express (int): The express flag indicating the position of the time period relative to other time periods (-1 for before, 0 for within, 1 for after).

    Properties:
        interval (tuple): The standardized interval format of the time period.
        time_span (list): The start and end years of the time period.
        iso_format (str): The ISO 8601 formatted string representation of the time period.

    Methods:
        set_additions(additions): Sets additional flags for the time period.
        take(x, type, ignore_errors): Adjusts the time period based on the specified parameters.

    """

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
            elif isinstance(arg, tuple):  # Assuming interval is a tuple of date objects
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
        """
        Combines multiple intervals into a single interval.

        Args:
            intervals (list): List of intervals to be combined.

        Returns:
            tuple: The combined interval.

        """
        # Initialize with extreme dates
        earliest_start = date.max
        latest_end = date.min

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
        """
        Adjusts the time period based on the specified period type and value.

        Args:
            x (int or str): The value specifying the period.
            type (str): The type of period (quarter, third, half).

        Raises:
            ValueError: If the value of x is invalid for the specified type.

        """
        max_value = {"quarter": 4, "third": 3, "half": 2}.get(type, 10)

        if x == "last":
            x = max_value
        elif x == "first":
            x = 1
        elif not 1 <= x <= max_value:
            raise ValueError(f"Invalid value for x based on type '{type}'")

        start_date, end_date = self._interval
        n_years = (end_date - start_date).days / 365.25
        step = round(n_years / max_value)

        if start_date.year < 0:  # Handling BC dates
            new_start_date = end_date - timedelta(days=(x - 1) * step * 365.25)
            new_end_date = end_date - timedelta(days=x * step * 365.25 - 1)
        else:
            new_start_date = start_date + timedelta(days=(x - 1) * step * 365.25)
            new_end_date = start_date + timedelta(days=x * step * 365.25 - 1)

        self._interval = (new_start_date, new_end_date)

    @property
    def interval(self):
        """
        Gets the standardized interval format of the time period.

        Returns:
            tuple: The standardized interval format.

        """
        if self._interval is None:
            return None

        # Standardize interval format (placeholder for actual logic)
        standardized_interval = (
            self._interval
        )  # Replace with actual standardization logic

        if self.express != 0:
            if self.express < 0:
                start_x = date.min
                end_x = standardized_interval[0] - timedelta(days=1)
            elif self.express > 0:
                start_x = standardized_interval[1] + timedelta(days=1)
                end_x = date.max

            standardized_interval = (start_x, end_x)

        return standardized_interval

    @property
    def time_span(self):
        """
        Gets the start and end years of the time period.

        Returns:
            list: The start and end years.

        """
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
        """
        Gets the ISO 8601 formatted string representation of the time period.

        Returns:
            str: The ISO 8601 formatted string.

        """
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
        """
        Sets additional flags for the time period.

        Args:
            additions (list): List of additional flags.

        Returns:
            Period: The updated Period object.

        """
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
        """
        Adjusts the time period based on the specified parameters.

        Args:
            x (int or str): The value specifying the period.
            type (str): The type of period (early, mid, late, quarter, third, half).
            ignore_errors (bool): Whether to ignore errors and return the original Period object.

        Returns:
            Period: The adjusted Period object.

        Raises:
            ValueError: If the specified type is unsupported.

        """
        try:
            # Ensure type is a string or None
            if type is not None:
                type = str(type).lower()

            if type in ["early", "mid", "late"]:
                method_name = f"_take_{type}"
                if hasattr(self, method_name):
                    self._interval = getattr(self, method_name)()
                else:
                    raise ValueError(f"Unsupported type: {type}")
            elif type in ["quarter", "third", "half"]:
                self._take_period(x, type)
            else:
                # Handle cases where type is None or x defines a year or decade
                if x is not None:
                    # Placeholder for logic to handle numerical value of x
                    # This part needs to be implemented based on specific requirements
                    pass

            # Create and return a new Periods object with adjusted interval
            return Period(self._interval)
        except Exception as e:
            if ignore_errors:
                return self
            else:
                raise e
