import re
import logging
from langdetect import detect, LangDetectException
from languages import LanguageProcessor


def unstruwwel(unprocessed_date, language=None, verbose=True, scheme="time-span"):
    """
    Unstruwwel function processes a list of input strings and performs various operations on them.

    Args:
        unprocessed_date (str): The input date to be processed.
        language (str or None, optional): The language of the input string. If None, language detection will be performed. Defaults to None.
        verbose (bool, optional): Whether to display verbose output. Defaults to True.
        scheme (str, optional): The scheme to use for processing dates. Valid options are "iso-format", "time-span", and "object". Defaults to "time-span".

    Returns:
        list: The processed dates.

    Raises:
        AssertionError: If the input is not valid.

    """
    logging.basicConfig(level=logging.INFO)

    # Validate input
    assert isinstance(verbose, bool), "verbose must be a boolean"
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    assert (
        isinstance(unprocessed_date, str) and len(unprocessed_date) > 0
    ), "unprocessed_date must be a non-empty string"
    assert scheme in ["iso-format", "time-span", "object"], "Invalid scheme"

    # Language detection and validation (needs implementation)
    if language is None:
        try:
            language = detect(unprocessed_date)
            logging.info("Language detected: %s", language)
        except LangDetectException as e:
            logging.error("Language detection failed, setting to 'en': %s", e)
            language = "en"

    standardized_input = standardize_string(unprocessed_date, language)
    logging.info("Standardized input: %s", standardized_input)
    processed_dates = []
    return processed_dates


def standardize_string(input_string, language_name, remove=None):
    """
    Standardizes a string based on the specified language.

    Args:
        input_string (str): The input string to be standardized.
        language_name (str): The name of the language.
        remove (list or None, optional): List of words to remove from the string. Defaults to None.

    Returns:
        str: The standardized string.
    """
    # Initialize the LanguageProcessor and load the language data
    language_processor = LanguageProcessor()
    language = language_processor.get_language(language_name)

    # Construct the list of words to remove
    remove = remove or []
    remove.extend(language["stop_words"])

    # Remove the words
    if remove:
        remove_regex = "|".join(map(re.escape, remove))
        input_string = re.sub(remove_regex, "", input_string)

    # Get the replacements
    replacements = language["replacements"]

    # Replace using the replacements
    for replacement in replacements:
        pattern = replacement["pattern"]
        input_string = re.sub(pattern, replacement["after"], input_string)

    # Squish spaces (replace multiple spaces with a single space)
    input_string = re.sub(r"\s+", " ", input_string).strip()

    return input_string


def extract_groups(text):
    """
    Extracts groups from a text using regular expressions.

    Args:
        text (str): The input text.

    Returns:
        list: The extracted groups.

    """
    capture_groups = r"([0-9]+)|([^\W\d_]+)|(\?)"
    matches = re.findall(capture_groups, text)
    # re.findall returns tuples, so we need to filter out empty matches
    matches = ["".join(match) for match in matches]
    return matches


if __name__ == "__main__":
    unstruwwel("late 16th century", verbose=True)
