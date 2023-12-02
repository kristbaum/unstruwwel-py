from unstruwwel.period import Period


def get_period(x, uncertain=False):
    """
    Get the period from a given input.

    Args:
        x (str): The input string.
        uncertain (bool, optional): Flag indicating if the period is uncertain. Defaults to False.

    Returns:
        str: The extracted period.

    """
    x = x[max(0, len(x) - 4) :]

    if uncertain:
        x = ["?"] + x

    if len(x) > 1:
        y = x[-2:][::-1]  # Equivalent to rev(x)[1:2] in R
        n_char = [len(char) for char in y]

        if n_char[0] < n_char[1]:
            add_char = y[1][: n_char[1] - n_char[0]]
            x[-1] = add_char + y[0]

    # Placeholder for Periods class instantiation and set_additions method
    x_date = Period(x).set_additions(x)

    return x_date
