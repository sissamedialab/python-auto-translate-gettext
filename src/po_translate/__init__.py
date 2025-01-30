#!/usr/bin/env python3
"""
Translate gettext .po files with DeepL.

Inspired by https://github.com/confdnt/python-auto-translate-gettext

"""

import argparse
import configparser
import logging
import pathlib
import re
import sys

import deepl
import polib

logger = logging.getLogger(__name__)


def parse_arguments() -> None:
    parser = argparse.ArgumentParser(description="Translate .po files using DeepL API.")

    # Required arguments
    parser.add_argument(
        "-f",
        "--file",
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
        help="Path to the .ini configuration file containing the API token. Defaults to './config.ini'.",
    )

    return parser.parse_args()


def read_api_token(config_path: str) -> str:
    """
    Reads the DeepL API token from the specified .ini file.

    Returns the API token as a string.
    """
    config = configparser.ConfigParser()

    if not pathlib.Path.isfile(config_path):
        logger.error(
            f"Error: Configuration file '{config_path}' does not exist.",
            file=sys.stderr,
        )
        sys.exit(1)

    config.read(config_path)

    try:
        api_token = config.get("deepL", "api_token")
    except (configparser.NoSectionError, configparser.NoOptionError):
        logger.exception("Error reading API token.", file=sys.stderr)
        sys.exit(1)
    return api_token


def translate(text: str, lang: str, translator: deepl.translator.Translator) -> str:
    """
    Translates the given text to the target language using the provided translator.

    Handles placeholders in the text to prevent them from being altered during translation.
    Returns the translated text.
    """
    placeholders = {}
    tokens = re.findall(r"%\((.*?)\)s", text)
    # FIXME: use regexp that allows for f-string's {}

    # Replace each token with a unique placeholder
    for i, token in enumerate(tokens):
        placeholder = f"__PLACEHOLDER_{i}__"
        placeholders[placeholder] = f"%({token})s"
        text = text.replace(f"%({token})s", placeholder)

    # Perform the translation
    try:
        translated_text = translator.translate_text(text, target_lang=lang)
    except deepl.DeepLException:
        logger.exception("DeepL translation error", file=sys.stderr)
        sys.exit(1)

    # Replace the placeholders back with the original tokens
    for placeholder, token in placeholders.items():
        translated_text = translated_text.replace(placeholder, token)

    return translated_text


def process_file(filename: str, lang: str, api_token: str) -> None:
    """
    Processes the .po file: translates untranslated entries and marks them as fuzzy.

    Saves the updated .po file.
    """
    if not pathlib.Path.resolve(filename):
        logger.error(f"Error: File '{filename}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        po = polib.pofile(filename)
    except Exception:
        logger.exception("Error reading .po file", file=sys.stderr)
        sys.exit(1)

    translator = deepl.Translator(api_token)
    translated_count = 0

    for entry in po.untranslated_entries():
        if not entry.msgstr:
            logger.debug(f"Translating entry: {entry.msgid}")
            translated_text = translate(entry.msgid, lang, translator)
            entry.msgstr = translated_text
            entry.fuzzy = True  # Mark as fuzzy
            translated_count += 1
            logger.debug(f"Translated to: {translated_text}\n")

    if translated_count > 0:
        try:
            po.save(filename)
            logger.debug(
                f"Successfully translated {translated_count} entries and saved to '{filename}'.",
            )
        except Exception:
            logger.exception("Error saving .po file", file=sys.stderr)
            sys.exit(1)
    else:
        logger.info("No untranslated entries found.")


def main() -> None:
    args = parse_arguments()
    config_path = pathlib.Path.resolve(args.config)
    api_token = read_api_token(config_path)

    # Validate target language (basic check for two-letter ISO code)
    if not re.fullmatch(r"[A-Z]{2}", args.language.upper()):
        logger.error(
            "Error: Target language must be a two-letter ISO code (e.g., DE, FR).",
            file=sys.stderr,
        )
        sys.exit(1)

    po_file_path = pathlib.Path.resolve(args.file)
    process_file(po_file_path, args.language.upper(), api_token)


if __name__ == "__main__":
    main()
