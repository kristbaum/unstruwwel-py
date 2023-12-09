import logging
from century import Century
from decade import Decade
from year import Year
import utils


class DateParser:
    def get_dates(self, date_parts, scheme="time-span"):
        """
        Process the input date and return the corresponding time span or ISO format.

        Args:
            x (list): List of strings representing the date.
            scheme (str): Output format, either 'time-span' or 'iso-format'.
            fuzzify (tuple): A tuple indicating the fuzziness of the date.

        Returns:
            The processed date in the specified format.
        """
        logging.info("Processing date: %s with schema: %s", date_parts, scheme)

        # Check for 'century' or a year in x
        if "century" in date_parts or any(utils.is_year(item) for item in date_parts):
            # Process the date based on whether it's a century, decade, or year
            if "century" in date_parts:
                date_obj = self.get_century(date_parts, negative=False, uncertain=False)
            elif any(item.endswith("s") for item in date_parts):
                date_obj = self.get_decade(date_parts, uncertain=False)
            else:
                date_obj = self.get_year(date_parts, negative=False, uncertain=False)

            # Return the date in the specified format
            return self.format_date(date_obj, scheme)
        else:
            # Return NA or None based on the scheme
            return [None, None] if scheme == "time-span" else None

    def format_date(self, date_obj, scheme):
        """
        Format the date object based on the specified scheme.

        Args:
            date_obj: The date object to be formatted.
            scheme (str): The scheme to format the date ('time-span' or 'iso-format').

        Returns:
            The formatted date.
        """
        if scheme == "time-span":
            return date_obj.time_span
        elif scheme == "iso-format":
            return date_obj.iso_format
        else:
            raise ValueError("Invalid scheme specified.")

    def get_century(self, date_parts, negative=False, uncertain=False):
        """
        Process the century from the date parts.

        Args:
            date_parts (list): List of strings representing the date.
            negative (bool): True if the date is BC, False otherwise.
            uncertain (bool): True if the date is uncertain, False otherwise.

        Returns:
            Century object with the processed century information.
        """
        logging.debug("Processing century: %s", date_parts)
        century_part = [part for part in date_parts if utils.is_year(part)]
        if not century_part:
            raise ValueError("No valid century part found.")

        # Extract the century value
        century_value = int(century_part[0])
        if negative:
            century_value = -century_value

        century = Century(century_value)

        # Apply additions and uncertainties
        additions = [part for part in date_parts if part not in century_part]
        century.set_additions(additions)
        if uncertain:
            century.fuzzy = -1  # Assuming -1 denotes uncertainty

        return century

    def get_decade(self, date_parts, uncertain=False):
        """
        Process the decade from the date parts.

        Args:
            date_parts (list): List of strings representing the date.
            uncertain (bool): True if the date is uncertain, False otherwise.

        Returns:
            Decade object with the processed decade information.
        """
        decade_part = [part for part in date_parts if utils.is_year(part)]
        if not decade_part:
            raise ValueError("No valid decade part found.")

        # Extract the decade value
        decade_value = int(decade_part[0])
        decade = Decade(decade_value)

        # Apply uncertainties if present
        if uncertain:
            decade.fuzzy = -1  # Assuming -1 denotes uncertainty

        return decade

    def get_year(self, date_parts, negative=False, uncertain=False):
        """
        Process the year from the date parts.

        Args:
            date_parts (list): List of strings representing the date.
            negative (bool): True if the year is BC (Before Christ), False otherwise.
            uncertain (bool): True if the year is uncertain, False otherwise.

        Returns:
            Year object with the processed year information.
        """
        year_part = [part for part in date_parts if utils.is_year(part)]
        if not year_part:
            raise ValueError("No valid year part found.")

        # Extract the year value
        year_value = int(year_part[0])
        if negative:
            year_value = -year_value  # Convert to negative for BC dates

        year = Year(year_value)

        # Apply uncertainties if present
        if uncertain:
            year.fuzzy = -1  # Assuming -1 denotes uncertainty

        return year
