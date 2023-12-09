import re
import logging
from langdetect import detect, LangDetectException
from languages import LanguageProcessor
from date_parser import DateParser


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
    extracted_groups = extract_groups(standardized_input)
    logging.info(extracted_groups)
    parser = DateParser()
    result = parser.get_dates(extracted_groups, scheme=scheme)
    logging.info("Result: %s", result)
    return result


def standardize_string(input_string, language_name, remove=None):
    """
    Standardizes a string based on the specified language. It involves removing specified words,
    applying language-specific replacements, and squishing multiple spaces into a single space.

    Args:
        input_string (str): The input string to be standardized.
        language_name (str): The name of the language for which the standardization rules apply.
        remove (list or None, optional): Additional list of words to remove from the string. Defaults to None.

    Returns:
        str: The standardized string.
    """
    logging.debug("Standardizing string: %s", input_string)
    language_processor = LanguageProcessor()
    language = language_processor.get_language(language_name)

    remove = remove or []

    # Extend the 'remove' list with stop words specific to the chosen language.
    # Stop words are common words in a language that are often filtered out in language processing.
    remove.extend(language["stop_words"])

    # If there are words to remove, construct a regular expression pattern to match them.
    # 're.escape' is used to escape any special characters in the words to remove.
    if remove:
        remove_regex = "|".join(map(re.escape, remove))

        # Apply the regex pattern to remove the matching words from the input string.
        input_string = re.sub(remove_regex, "", input_string)

    # Retrieve the list of replacement patterns defined for the language.
    # These patterns specify how certain words or phrases should be altered.
    replacements = language["replacements"]

    # Iterate over each replacement rule and apply it to the input string.
    # 're.sub' is used to find and replace patterns defined in 'replacements'.
    for replacement in replacements:
        input_string = re.sub(
            replacement["pattern"], replacement["after"], input_string
        )

    # Finally, squish multiple spaces into a single space and trim leading/trailing spaces.
    # This is done to clean up any irregular spacing caused by the earlier replacements.
    input_string = re.sub(r"\s+", " ", input_string).strip()

    # Return the standardized string.
    return input_string


def extract_groups(text):
    """
    Extracts groups from a text using regular expressions.

    Args:
        text (str): The input text.

    Returns:
        list: The extracted groups.

    """
    logging.debug("Extracting groups from text: %s", text)
    capture_groups = r"([0-9]+)|([^\W\d_]+)|(\?)"
    matches = re.findall(capture_groups, text)
    # re.findall returns tuples, so we need to filter out empty matches
    matches = ["".join(match) for match in matches]
    return matches


if __name__ == "__main__":
    unstruwwel("1650", scheme="iso-format", verbose=True)
