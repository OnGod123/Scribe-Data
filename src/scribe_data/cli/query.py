"""
Functions for querying languages-data types packs for the Scribe-Data CLI.

.. raw:: html
    <!--
    * Copyright (C) 2024 Scribe
    *
    * This program is free software: you can redistribute it and/or modify
    * it under the terms of the GNU General Public License as published by
    * the Free Software Foundation, either version 3 of the License, or
    * (at your option) any later version.
    *
    * This program is distributed in the hope that it will be useful,
    * but WITHOUT ANY WARRANTY; without even the implied warranty of
    * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    * GNU General Public License for more details.
    *
    * You should have received a copy of the GNU General Public License
    * along with this program.  If not, see <https://www.gnu.org/licenses/>.
    -->
"""

import os


from scribe_data.wikidata.update_data import update_data
from scribe_data.cli.convert import export_json
from scribe_data.cli.convert import export_csv_or_tsv
from pathlib import Path
from typing import Optional

DATA_DIR = Path("scribe_data_json_export")


def query_data(
    language: Optional[str] = None,
    data_type: Optional[str] = None,
    output_dir: Optional[str] = None,
    overwrite: bool = False,
    output_type: Optional[str] = None,
    all: bool = False,
) -> None:
    if all:
        print("Updating all languages and data types ...")
        update_data()

    elif language or data_type:
        languages = [language] if language else None
        data_type = [data_type] if data_type else None
        print(f"Updating data for language: {language}, data type: {data_type}")
        update_data(languages, data_type)

    else:
        raise ValueError(
            "You must provide either a --language (-l) or --data-type (-dt) option, or use --all (-a)."
        )

    if output_dir:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        if output_type == "json" or output_type is None:
            export_json(language, data_type, output_dir, overwrite)

        elif output_type in ["csv", "tsv"]:
            export_csv_or_tsv(language, data_type, output_dir, overwrite, output_type)

        else:
            raise ValueError(
                "Unsupported output type. Please use 'json', 'csv', or 'tsv'."
            )

    else:
        print(
            "Data update complete. No output directory specified for exporting results."
        )
        print(
            f"Updated data can be found in: {os.path.abspath('scribe_data_json_export')}"
        )

    # Check if data was actually updated
    data_path = Path("scribe_data_json_export")
    if language:
        lang_path = data_path / language.capitalize()
        if not lang_path.exists():
            print(f"Warning: No data directory found for language '{language}'")

        elif data_type:
            dt_file = lang_path / f"{data_type}.json"
            if not dt_file.exists():
                print(f"Warning: No data file found for '{language}' {data_type}")

        else:
            print(f"Data updated for language: {language}")
    elif data_type:
        dt_updated = False
        for lang_dir in data_path.iterdir():
            if lang_dir.is_dir() and (lang_dir / f"{data_type}.json").exists():
                dt_updated = True
                break

        if not dt_updated:
            print(f"Warning: No data files found for data type '{data_type}'")

        else:
            print(f"Data updated for data type: {data_type}")
