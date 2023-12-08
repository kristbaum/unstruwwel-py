import json
import os
import logging
import glob


class LanguageProcessor:
    def __init__(self, data_path="./data-raw"):
        """
        Initialize the LanguageProcessor class.

        Parameters:
        - data_path (str): The path to the directory containing the language JSON files. Default is "./data-raw".
        """
        self.languages = None
        self.load_languages(data_path)

    @staticmethod
    def get_search_variants(input_str):
        """
        Generate search variants for a given string.

        Parameters:
        - input_str (str): The input string.

        Returns:
        - regex (str): The regular expression pattern for the search variants.
        """
        variants = [
            f"[{char}|{char.upper()}]{input_str[i+1:]}"
            for i, char in enumerate(input_str)
            if i < len(input_str) - 1
        ]
        valid_chars = r"^\p{L}"  # unicode-friendly
        regex = "|".join(
            [
                f"(?<=[{valid_chars}]|^){variant}(?=[{valid_chars}]|$)"
                for variant in variants
            ]
        )
        return regex

    def get_language(self, file_path):
        """
        Get the language details from a JSON file.

        Parameters:
        - file_path (str): The path to the JSON file.

        Returns:
        - dict: Language details including name, date_order, stop_words, simplifications, and replacements.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            language_data = json.load(file)

        language_details = {
            "name": language_data["name"].lower(),
            "date_order": language_data["date_order"],
            "stop_words": [
                self.get_search_variants(word.lower())
                for word in language_data["stop_words"]
            ],
            "simplifications": [
                {
                    "before": simplification.lower(),
                    "after": self.get_search_variants(simplification.lower()),
                }
                for simplification in language_data["simplifications"]
            ],
        }
        logging.debug("Language details: %s", json.dumps(language_details, indent=4))

        replacement_list = [
            {
                "before": key.lower(),
                "after": value,
                "pattern": self.get_search_variants(key.lower()),
            }
            for key, value in language_data.items()
            if key not in language_details
        ]

        language_details["replacements"] = replacement_list

        return language_details

    def add_language(self, language_name, path):
        """
        Add a new language JSON file.

        Parameters:
        - language_name (str): The name of the language.
        - path (str): The path to the directory containing the language JSON files.
        """
        files = glob.glob(os.path.join(path, "*.json"))
        wrappers = []

        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                content = json.load(f)
                wrapper = {
                    k: (v if isinstance(v, list) else [""]) for k, v in content.items()
                }
                wrappers.append(wrapper)

        if wrappers:
            # Find the wrapper with the most keys
            index = max(range(len(wrappers)), key=lambda i: len(wrappers[i]))
            new_language_data = wrappers[index]

            # Save new language file
            with open(
                os.path.join(path, f"{language_name}.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(new_language_data, f, indent=4)

    def load_languages(self, data_path):
        """
        Load the language JSON files.

        Parameters:
        - data_path (str): The path to the directory containing the language JSON files.
        """
        language_files = [f for f in os.listdir(data_path) if f.endswith(".json")]
        logging.info("Loading language files: %s", language_files)

        self.languages = {}
        for file in language_files:
            file_path = os.path.join(data_path, file)
            language_data = self.get_language(file_path)
            self.languages[language_data["name"]] = language_data["details"]
