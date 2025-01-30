#!/usr/bin/env python3

import polib
import deepl
import argparse
import configparser
import os
import sys
import re

def parse_arguments():
    """
    Parses command-line arguments using argparse.
    Returns the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Translate .po files using DeepL API.")

    # Required arguments
    parser.add_argument(
        "-f", "--file",
        required=True,
        help="Path to the .po file to translate."
    )

    parser.add_argument(
        "-l", "--language",
        required=True,
        help="Target language as a two-letter ISO code (e.g., DE for German)."
    )

    # Optional argument for config file
    parser.add_argument(
        "--config",
        default="config.ini",
        help="Path to the .ini configuration file containing the API token. Defaults to './config.ini'."
    )

    return parser.parse_args()

def read_api_token(config_path):
    """
    Reads the DeepL API token from the specified .ini file.
    Returns the API token as a string.
    """
    config = configparser.ConfigParser()

    if not os.path.isfile(config_path):
        print(f"Error: Configuration file '{config_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    config.read(config_path)

    try:
        api_token = config.get("deepL", "api_token")
        if not api_token:
            raise configparser.NoOptionError("api_token", "deepL")
        return api_token
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        print(f"Error reading API token: {e}", file=sys.stderr)
        sys.exit(1)

def translate(text, lang, translator):
    """
    Translates the given text to the target language using the provided translator.
    Handles placeholders in the text to prevent them from being altered during translation.
    Returns the translated text.
    """
    # Define a dictionary to hold the mappings of tokens to placeholders
    placeholders = {}

    # Use a regular expression to find all the tokens, e.g., %(token)s
    tokens = re.findall(r'%\((.*?)\)s', text)

    # Replace each token with a unique placeholder
    for i, token in enumerate(tokens):
        placeholder = f'__PLACEHOLDER_{i}__'
        placeholders[placeholder] = f'%({token})s'
        text = text.replace(f'%({token})s', placeholder)

    # Perform the translation
    try:
        translated_text = translator.translate_text(text, target_lang=lang)
    except deepl.DeepLException as e:
        print(f"DeepL translation error: {e}", file=sys.stderr)
        sys.exit(1)

    # Replace the placeholders back with the original tokens
    for placeholder, token in placeholders.items():
        translated_text = translated_text.replace(placeholder, token)

    return translated_text

def process_file(filename, lang, api_token):
    """
    Processes the .po file: translates untranslated entries and marks them as fuzzy.
    Saves the updated .po file.
    """
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        po = polib.pofile(filename)
    except Exception as e:
        print(f"Error reading .po file: {e}", file=sys.stderr)
        sys.exit(1)

    translator = deepl.Translator(api_token)
    translated_count = 0

    for entry in po.untranslated_entries():
        if not entry.msgstr:
            print(f"Translating entry: {entry.msgid}")
            translated_text = translate(entry.msgid, lang, translator)
            entry.msgstr = translated_text
            entry.fuzzy = True  # Mark as fuzzy
            translated_count += 1
            print(f"Translated to: {translated_text}\n")

    if translated_count > 0:
        try:
            po.save(filename)
            print(f"Successfully translated {translated_count} entries and saved to '{filename}'.")
        except Exception as e:
            print(f"Error saving .po file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No untranslated entries found.")

def main():
    args = parse_arguments()

    # Resolve the absolute path for the config file
    config_path = os.path.abspath(args.config)

    # Read the API token from the config file
    api_token = read_api_token(config_path)

    # Validate target language (basic check for two-letter ISO code)
    if not re.fullmatch(r'[A-Z]{2}', args.language.upper()):
        print("Error: Target language must be a two-letter ISO code (e.g., DE, FR).", file=sys.stderr)
        sys.exit(1)

    # Resolve the absolute path for the .po file
    po_file_path = os.path.abspath(args.file)

    # Process the .po file
    process_file(po_file_path, args.language.upper(), api_token)

if __name__ == "__main__":
    main()
