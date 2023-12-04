import json
import pandas as pd
import re
import os
import glob


def get_search_variants(x):
    variants = [
        f"[{char}|{char.upper()}]{x[i+1:]}"
        for i, char in enumerate(x)
        if i < len(x) - 1
    ]
    valid_chars = r"^\p{L}"  # unicode-friendly
    regex = "|".join(
        [
            f"(?<=[{valid_chars}]|^){variant}(?=[{valid_chars}]|$)"
            for variant in variants
        ]
    )
    return regex


def get_language(file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    language = {
        "name": data["name"].lower(),
        "date_order": data["date_order"],
        "stop_words": [
            get_search_variants(word.lower()) for word in data["stop_words"]
        ],
        "simplifications": pd.DataFrame(
            {
                "before": [s.lower() for s in data["simplifications"]],
                "after": [
                    get_search_variants(s.lower()) for s in data["simplifications"]
                ],
            }
        ),
    }

    replacements = pd.DataFrame(
        {
            "before": [k.lower() for k in data.keys()],
            "after": [
                v
                for sublist in [[k] * len(v) for k, v in data.items()]
                for v in sublist
            ],
        }
    )
    replacements = replacements[~replacements["after"].isin(language.keys())]
    replacements["pattern"] = replacements["before"].apply(get_search_variants)

    language["replacements"] = replacements

    return language


def add_language(language, path):
    files = glob.glob(os.path.join(path, "*.json"))
    wrappers = []

    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            content = json.load(f)
            wrapper = {
                k: (v if isinstance(v, list) else [""]) for k, v in content.items()
            }
            wrappers.append(wrapper)

    index = max(range(len(wrappers)), key=lambda i: len(wrappers[i]))
    with open(os.path.join(path, f"{language}.json"), "w", encoding="utf-8") as f:
        json.dump(wrappers[index], f, indent=4)


# Load languages
language_files = glob.glob("./data-raw/*.json")
languages = pd.concat([get_language(file) for file in language_files])

# use_data equivalent in Python might involve writing the languages dataframe to a file
languages.to_csv("languages.csv", index=False)
