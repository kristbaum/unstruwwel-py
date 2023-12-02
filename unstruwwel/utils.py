from datetime import datetime, timedelta


def is_valid_language(x, languages):
    """
    Check if all elements in x are valid languages.

    Args:
        x (list): List of languages to check.
        languages (list): List of valid languages.

    Returns:
        bool: True if all elements in x are valid languages, False otherwise.
    """
    return all(lang in languages for lang in x)


def get_invalid_language(x, languages):
    """
    Get the first invalid language in x.

    Args:
        x (list): List of languages to check.
        languages (list): List of valid languages.

    Returns:
        str or None: The first invalid language in x, or None if all languages are valid.
    """
    return next((lang for lang in x if lang not in languages), None)


def get_months():
    """
    Get a list of all months.

    Returns:
        list: List of month names.
    """
    return [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]


def get_current_year():
    """
    Get the current year.

    Returns:
        int: The current year.
    """
    return datetime.now().year


def is_year(x):
    """
    Check if x is a valid year.

    Args:
        x (int): The year to check.

    Returns:
        bool: True if x is a valid year, False otherwise.
    """
    return str(x) in [str(year) for year in range(100, 2901)]


def is_year_addition(x):
    """
    Check if x is a valid year addition.

    Args:
        x (int): The year addition to check.

    Returns:
        bool: True if x is a valid year addition, False otherwise.
    """
    return str(x) in [str(year) for year in range(1, 100)]


def is_number(x):
    """
    Check if x is a number.

    Args:
        x (str): The value to check.

    Returns:
        bool: True if x is a number, False otherwise.
    """
    try:
        float(x)
        return True
    except ValueError:
        return False


def get_item(x, n=1):
    """
    Get the nth item from x.

    Args:
        x (list): The list to get the item from.
        n (int, optional): The index of the item to get. Defaults to 1.

    Returns:
        Any: The nth item from x.
    """
    return x[n - 1]


def generate_date_range(start, end):
    """
    Generate a list of dates between start and end.

    Args:
        start (str): The start date in the format 'YYYY-MM-DD'.
        end (str): The end date in the format 'YYYY-MM-DD'.

    Returns:
        list: List of dates between start and end.
    """
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    return [
        (start_date + timedelta(days=x)).strftime("%Y-%m-%d")
        for x in range((end_date - start_date).days + 1)
    ]
