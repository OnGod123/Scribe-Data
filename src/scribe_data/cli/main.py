#!/usr/bin/env python3
import argparse
from pathlib import Path
from scribe_data.cli.cli_utils import validate_language_and_data_type
from scribe_data.cli.convert import convert_wrapper
from scribe_data.cli.get import get_data
from scribe_data.cli.interactive import start_interactive_mode
from scribe_data.cli.list import list_wrapper
from scribe_data.cli.total import total_wrapper
from scribe_data.cli.upgrade import upgrade_cli
from scribe_data.cli.version import get_version_message
from scribe_data.cli.db_utils.insert_translation import insert_translation
from scribe_data.cli.db_utils.meli_search_db import create_index, check_index_exists, add_documents
from scribe_data.cli.db_utils.search_database import search_by_meilisearch
from scribe_data.cli.db_utils.postgrel import create_table
from scribe_data.cli.db_utils.common_utils import get_q_number, get_word_translations, get_sentence_translations
from scribe_data.cli.db_utils.search_wiki_db import check_internet_connection, get_translations_for_word


def main() -> None:
    # Constants for descriptions
    LIST_DESCRIPTION = "List languages, data types and combinations of each that Scribe-Data can be used for."
    GET_DESCRIPTION = "Get data from Wikidata and other sources for the given languages and data types."
    TOTAL_DESCRIPTION = "Check Wikidata for the total available data for the given languages and data types."
    CONVERT_DESCRIPTION = "Convert data returned by Scribe-Data to different file types."
    CLI_EPILOG = "Visit the codebase at https://github.com/scribe-org/Scribe-Data and documentation at https://scribe-data.readthedocs.io to learn more!"

    # Setup main parser
    parser = argparse.ArgumentParser(
        description="The Scribe-Data CLI is a tool for extracting language data from Wikidata and other sources.",
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{get_version_message()}",
        help="Show the version of the Scribe-Data CLI.",
    )

    parser.add_argument(
        "-u",
        "--upgrade",
        action="store_true",
        help="Upgrade the Scribe-Data CLI to the latest version.",
    )

    # Create translation parser
    translation_parser = subparsers.add_parser(
        "translate",
        help="Translate words or phrases between multiple languages."
    )
    translation_parser.add_argument(
        '-s', '--source-lang',
        choices=['en', 'es', 'pt', 'fr', 'de'],
        required=True,
        help="Source language for translation, e.g., 'en' for English."
    )
    translation_parser.add_argument(
        '-t', '--target-lang',
        nargs='+',  # Allow multiple target languages
        choices=['en', 'es', 'pt', 'fr', 'de'],
        required=True,
        help="Target language(s) for translation, e.g., 'pt' for Portuguese."
    )
    translation_parser.add_argument(
        'phrase',
        type=str,
        help="Word or phrase to translate."
    )

    # MARK: List
    list_parser = subparsers.add_parser(
        "list",
        aliases=["l"],
        help=LIST_DESCRIPTION,
        description=LIST_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    list_parser.add_argument("-lang", "--language", nargs="?", const=True, help="List options for all or given languages.")
    list_parser.add_argument("-dt", "--data-type", nargs="?", const=True, help="List options for all or given data types (e.g., nouns, verbs).")
    list_parser.add_argument("-a", "--all", action=argparse.BooleanOptionalAction, help="List all languages and data types.")

    # MARK: GET
    get_parser = subparsers.add_parser(
        "get",
        aliases=["g"],
        help=GET_DESCRIPTION,
        description=GET_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    get_parser.add_argument("-lang", "--language", type=str, help="The language(s) to get data for.")
    get_parser.add_argument("-dt", "--data-type", type=str, help="The data type(s) to get data for (e.g., nouns, verbs).")
    get_parser.add_argument("-ot", "--output-type", type=str, choices=["json", "csv", "tsv", "sqlite"], help="The output file type.")
    get_parser.add_argument("-od", "--output-dir", type=str, help="The output directory path for results.")
    get_parser.add_argument("-ope", "--outputs-per-entry", type=int, help="How many outputs should be generated per data entry.")
    get_parser.add_argument("-o", "--overwrite", action="store_true", help="Whether to overwrite existing files (default: False).")
    get_parser.add_argument("-a", "--all", action=argparse.BooleanOptionalAction, help="Get all languages and data types.")
    get_parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")

    # MARK: Total
    total_parser = subparsers.add_parser(
        "total",
        aliases=["t"],
        help=TOTAL_DESCRIPTION,
        description=TOTAL_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    total_parser.add_argument("-lang", "--language", type=str, help="The language(s) to check totals for.")
    total_parser.add_argument("-dt", "--data-type", type=str, help="The data type(s) to check totals for (e.g., nouns, verbs).")
    total_parser.add_argument("-a", "--all", action=argparse.BooleanOptionalAction, help="Check for all languages and data types.")

    # MARK: Convert
    convert_parser = subparsers.add_parser(
        "convert",
        aliases=["c"],
        help=CONVERT_DESCRIPTION,
        description=CONVERT_DESCRIPTION,
        epilog=CLI_EPILOG,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=60),
    )
    convert_parser.add_argument("-lang", "--language", type=str, required=True, help="The language of the file to convert.")
    convert_parser.add_argument("-dt", "--data-type", type=str, required=True, help="The data type(s) of the file to convert (e.g., nouns, verbs).")
    convert_parser.add_argument("-if", "--input-file", type=Path, required=True, help="The path to the input file to convert.")
    convert_parser.add_argument("-ot", "--output-type", type=str, choices=["json", "csv", "tsv", "sqlite"], required=True, help="The output file type.")
    convert_parser.add_argument("-od", "--output-dir", type=str, help="The directory where the output file will be saved.")
    convert_parser.add_argument("-o", "--overwrite", action="store_true", help="Whether to overwrite existing files (default: False).")
    convert_parser.add_argument("-ko", "--keep-original", action="store_true", default=True, help="Whether to keep the original file to be converted (default: True).")

    # Parse arguments
    args = parser.parse_args()

    # Safely check for data_type presence
    if hasattr(args, 'data_type') and args.data_type and isinstance(args.data_type, str):
        args.data_type = args.data_type.replace("-", "_")

    try:
        # Check for presence of 'language' before validation
        if (hasattr(args, 'language') and args.language) or (hasattr(args, 'data_type') and args.data_type):
            validate_language_and_data_type(language=args.language, data_type=args.data_type)
    except ValueError as e:
        print(f"Input validation failed with error: {e}")
        return

    if args.upgrade:
        upgrade_cli()
        return

    if not args.command:
        parser.print_help()
        return

    # Handle translation command
    if args.command == "translate":
        target_langs = [lang for lang in args.target_lang if lang != args.source_lang]
        if not target_langs:
            print("Error: Target language(s) must be different from the source language.")
            return

        # Convert args to a dictionary for easier handling
        args_dict = {
            "source_lang": args.source_lang,
            "target_lang": target_langs,
            "phrase": args.phrase,
        }

        # Search the database for an existing translation
        existing_translation = search_by_meilisearch(args_dict)

        # If no translation is found, perform a new translation
        if not existing_translation:
            print("No existing translation found. Translating...")

            # Determine whether to translate as a word or sentence
            if len(args.phrase.split()) == 1:
                # Single word translation
                translation = get_word_translations(args_dict)
                print(f"Translation: {translation}")
            else:
                # Multi-word (sentence) translation
                translation = get_sentence_translations(args_dict)
                print(f"Translation: {translation}")
        else:
            print(f"Found existing translation: {existing_translation}")

    # Handle other commands
    elif args.command == "list":
        list_wrapper(args)
    elif args.command == "get":
        get_data(args)
    elif args.command == "total":
        total_wrapper(args)
    elif args.command == "convert":
        convert_wrapper(args)
    else:
        print("Invalid command. Please check your inputs.")


if __name__ == "__main__":
    main()