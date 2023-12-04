import re
from langdetect import detect
import logging
from languages import languages

def unstruwwel(unprocessed_date, language=None, verbose=True, scheme="time-span"):
    """
    Unstruwwel function processes a list of input strings and performs various operations on them.

    Args:
        unprocessed_date (str): The input date to be processed.
        language (str or None, optional): The language the input String. If None, language detection will be performed. Defaults to None.
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
    assert isinstance(unprocessed_date, str) and len(unprocessed_date) > 0, "unprocessed_date must be a non-empty string"
    assert scheme in ["iso-format", "time-span", "object"], "Invalid scheme"

    # Language detection and validation (needs implementation)
    if language is None:
        language = [detect(unprocessed_date)]
        logging.info(f"Language detected: {language}")

    standardized_input = standardize_input([unprocessed_date], language)
    processed_dates = []
    return processed_dates


def standardize_string(x, language_name, remove=None):
    # Filter the language data
    language = languages[languages['name'] == language_name.lower()]

    # Construct the list of words to remove
    remove = remove or []
    for stop_words in language['stop_words'].iloc[0]:
        remove.extend(stop_words)

    # Remove the words
    if remove:
        remove_regex = '|'.join(map(re.escape, remove))
        x = re.sub(remove_regex, '', x)

    # Get the replacements
    replacements = language['replacements'].iloc[0]
    replacements = replacements[replacements['before'] != replacements['after']].drop_duplicates()

    # Replace using the replacements
    for _, row in replacements.iterrows():
        pattern = row['pattern']
        x = re.sub(pattern, row['after'], x)

    # Squish spaces (replace multiple spaces with a single space)
    x = re.sub(r'\s+', ' ', x).strip()

    return x


def extract_groups(text):
    capture_groups = r"([0-9]+)|([^\W\d_]+)|(\?)"
    matches = re.findall(capture_groups, text)
    # re.findall returns tuples, so we need to filter out empty matches
    matches = [''.join(match) for match in matches]
    return matches
