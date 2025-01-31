#!/usr/bin/env python3
"""
Translate gettext .po files with DeepL.

Inspired by https://github.com/confdnt/python-auto-translate-gettext

"""

import argparse
import configparser
import logging
import re
import sys

import colorlog
import deepl
import polib

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter("%(log_color)s%(levelname)s:%(name)s:%(message)s"),
)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(handler)
logger = logging.getLogger(__name__)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)


def parse_arguments() -> None:
    parser = argparse.ArgumentParser(description="Translate .po files using DeepL API.")

    # Required arguments
    parser.add_argument(
        "-f",
        "--file",
        type=argparse.FileType("r"),
        required=True,
        help="Path to the .po file to translate.",
    )

    parser.add_argument(
        "-l",
        "--language",
        required=True,
        help="Target language as a two-letter ISO code (e.g., DE for German).",
    )

    # Optional argument for config file
    parser.add_argument(
        "--config",
        default="config.ini",
        type=argparse.FileType("r"),
        help="Path to the .ini configuration file containing the API token. Defaults to '%(default)s'.",
    )

    return parser.parse_args()


def read_api_token(config_path: str) -> str:
    """
    Reads the DeepL API token from the specified .ini file.

    Returns the API token as a string.
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    try:
        api_token = config.get("deepL", "api_token")
    except (configparser.NoSectionError, configparser.NoOptionError):
        logger.exception("Error reading API token.")
        sys.exit(1)
    return api_token


def hide_variables(text: str) -> (str, dict):
    """Replace variables enbedded into the text with a placeholder."""
    # Manage f-strings and %-interpolated variables separately
    #
    # We use 1-char non-translatable placeholders in order
    # - avoid the placeholder beeing translated (sometimes it happened)
    # - reduce the number of billed-chars
    keys = [
        "🤦",
        "💆",
        "🧐",
        "😶",
        "😘",
        "😓",
        "🤠",
        "🙆",
        "😮",
    ]
    placeholders = {}
    tokens = re.findall(r"%\((.*?)\)s", text)
    i = 0
    for i, token in enumerate(tokens):
        placeholder = keys[i]  # yes, fail badly if we have many variables 😉
        placeholders[placeholder] = f"%({token})s"
        text = text.replace(f"%({token})s", placeholder)

    tokens = re.findall(r"\{(.*?)\}", text)
    for j, token in enumerate(tokens, start=i):
        placeholder = keys[j]
        placeholders[placeholder] = f"{{{token}}}"
        text = text.replace(f"{{{token}}}", placeholder)
    return text, placeholders


def unhide_variables(text: str, placeholders: dict) -> str:
    """Replace the placeholders back with the original tokens."""
    for placeholder, token in placeholders.items():
        text = text.replace(placeholder, token)
    return text


def translate(text: str, lang: str, translator: deepl.translator.Translator) -> str:
    """
    Translates the given text to the target language using the provided translator.

    Handles placeholders in the text to prevent them from being altered during translation.
    Returns the translated text.
    """
    prepared_text, placeholders = hide_variables(text)
    # Perform the translation
    try:
        translated_text = str(
            translator.translate_text(prepared_text, target_lang=lang),
        )
    except deepl.DeepLException:
        logger.exception("DeepL translation error")
        sys.exit(1)
    return unhide_variables(translated_text, placeholders)


def process_file(filename: str, lang: str, api_token: str) -> None:
    """
    Processes the .po file: translates untranslated entries and marks them as fuzzy.

    Saves the updated .po file.
    """
    try:
        po = polib.pofile(filename)
    except Exception:
        logger.exception("Error reading .po file")
        sys.exit(1)

    translator = deepl.Translator(api_token)
    translated_count = 0
    for entry in po.untranslated_entries():
        if not entry.msgstr:
            logger.debug(f"Translating entry: {entry.msgid}")
            translated_text = translate(entry.msgid, lang, translator)
            entry.msgstr = translated_text
            entry.flags.append("fuzzy")  # Mark as fuzzy
            translated_count += 1
            logger.debug(f"Translated to: {translated_text}")

    if translated_count > 0:
        try:
            po.save(filename)
            logger.debug(
                f"Successfully translated {translated_count} entries and saved to '{filename}'.",
            )
        except Exception:
            logger.exception("Error saving .po file")
            sys.exit(1)
    else:
        logger.info("No untranslated entries found.")


def main() -> None:
    args = parse_arguments()
    config_path = args.config.name
    api_token = read_api_token(config_path)

    # Validate target language (basic check for two-letter ISO code)
    if not re.fullmatch(r"[A-Z]{2}", args.language.upper()):
        logger.error(
            "Error: Target language must be a two-letter ISO code (e.g., DE, FR).",
        )
        sys.exit(1)

    po_file_path = args.file.name
    process_file(po_file_path, args.language.upper(), api_token)


if __name__ == "__main__":
    main()
