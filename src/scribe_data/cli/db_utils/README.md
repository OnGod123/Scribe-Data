Translation Tool
Overview
The Translation Tool allows users to translate words and phrases between multiple languages using the Wikidata SPARQL API. It supports dynamic fetching of Q-numbers for words and retrieves their translations in specified target languages.

Features
Word Translation: Translate single words to multiple languages.
Phrase Translation: Translate phrases consisting of multiple words.
Multiple Language Support: Translations available for French, Spanish, German, and Portuguese.
Dynamic Q-number Retrieval: Automatically fetches the Q-number for a given word from Wikidata.
Requirements
Python 3.x
Required libraries:
psycopg2
SPARQLWrapper
You can install the required libraries using pip:

bash
Copy code
pip install psycopg2 SPARQLWrapper
Usage
Command-Line Interface
The tool can be used from the command line, where you can specify the source and target languages, along with the phrase you want to translate.


python3 /path/to/main.py translate -s <source_language> -t <target_language> -- "<phrase>"
Parameters
-s <source_language>: Specify the source language (e.g., en for English).
-t <target_language>: Specify the target language (e.g., es for Spanish).
-- "<phrase>": The phrase you want to translate, enclosed in quotes. Use -- before the phrase to indicate the start of the phrase.
Example Usage
To translate the word "eat" from English to Spanish:


python3 /path/to/main.py translate -s en -t es -- "eat"
To translate the phrase "day check up" from English to Spanish:


python3 /path/to/main.py translate -s en -t es -- "day check up"
Notes
Ensure you have an active internet connection, as the tool fetches data from the Wikidata SPARQL API.
The tool will return translations for the specified word or phrase along with error messages if no translations are found or if there are issues with the input.
Error Handling
If the tool encounters any issues during execution, it will display appropriate error messages. Common errors may include:

Invalid input: Ensure the input phrase is a non-empty string.
Connection issues: Check your internet connection if the tool cannot fetch translations.
Example Output
For the command:



python3 /path/to/main.py translate -s en -t es -- "day check up"
The output may look like:



Translating word: 'day'
Translation: {'day': {'fr': 'jour', 'de': 'Tag', 'es': 'día', 'pt': 'dia'}}
Translating word: 'check'
Translation: {'check': {'fr': 'vérifier', 'de': 'prüfen', 'es': 'comprobar', 'pt': 'verificar'}}
Translating word: 'up'
Translation: {'up': {'fr': 'haut', 'de': 'hoch', 'es': 'arriba', 'pt': 'cima'}}
Contribution
If you'd like to contribute to the project, please submit a pull request or open an issue to discuss improvements or feature requests.

License
This project is licensed under the MIT License.
