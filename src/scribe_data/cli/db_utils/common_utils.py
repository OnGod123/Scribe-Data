import os
import socket
import psycopg2
from SPARQLWrapper import SPARQLWrapper, JSON

def check_internet_connection():
    """Check if there is an active internet connection."""
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        return False

def get_q_number(word):
    """Fetch the Q-number for the given word from Wikidata."""
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?item WHERE {{
        ?item rdfs:label "{word}"@en.
    }} LIMIT 1
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        print("Q-number query results:", results)  # Print raw results for debugging

        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["item"]["value"]
        else:
            print(f"No Q-number found for the word '{word}'.")
            return None
    except Exception as e:
        print(f"Error in fetching Q-number: {e}")
        return None

def get_translations_for_word(word, target_languages):
    """Get translations for a given word."""
    word_q = get_q_number(word)  # Get Q-number dynamically
    if not word_q:
        return None

    language_filter = ", ".join([f'"{lang}"' for lang in target_languages])

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?translation ?languageCode
    WHERE {{
        <{word_q}> rdfs:label ?translation.
        FILTER (LANG(?translation) IN ({language_filter}))
        BIND (LANG(?translation) AS ?languageCode)
    }}
    LIMIT 10
    """

    print("Translation SPARQL Query:")
    print(query)

    if not check_internet_connection():
        print("No internet connection. Please check your network settings.")
        return None

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        print("Translation query results:", results)  # Print raw translation results for debugging

        if not results["results"]["bindings"]:
            print(f"No translations found for '{word}' in the specified languages.")
            return None

        translations = {
            result["languageCode"]["value"]: result["translation"]["value"]
            for result in results["results"]["bindings"]
        }

        return translations

    except Exception as e:
        print(f"Error in query execution: {e}")
        return None

def get_translations_for_word_by_q_number(word_q, target_languages):
    """Get translations using the Q-number directly."""
    language_filter = ", ".join([f'"{lang}"' for lang in target_languages])

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?translation ?languageCode
    WHERE {{
        <{word_q}> rdfs:label ?translation.
        FILTER (LANG(?translation) IN ({language_filter}))
        BIND (LANG(?translation) AS ?languageCode)
    }}
    LIMIT 2
    """

    print("Translation SPARQL Query by Q-number:")
    print(query)

    if not check_internet_connection():
        print("No internet connection. Please check your network settings.")
        return None

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        print("Translation query results:", results)  # Print raw translation results for debugging

        if not results["results"]["bindings"]:
            print(f"No translations found for Q-number '{word_q}' in the specified languages.")
            return None

        translations = {
            result["languageCode"]["value"]: result["translation"]["value"]
            for result in results["results"]["bindings"]
        }

        return translations
    except Exception as e:
        print(f"Error in query execution: {e}")
        return None

def get_word_translations(input_data):
    """Get translations for a single word and return a dictionary."""
    # Check if input_data is a dict and extract 'phrase' if it is
    if isinstance(input_data, dict):
        word = input_data.get('phrase', '')
    else:
        word = input_data

    if not isinstance(word, str) or not word.strip():
        print(f"Invalid input: '{word}' is not a valid string.")
        return {str(word): "Error: word must be a non-empty string."}

    target_languages = ['fr', 'es', 'de', 'pt']  # Specify the target languages here
    translations = get_translations_for_word(word, target_languages)

    if translations:
        return {word: translations}
    else:
        return {word: f"No translations found for '{word}'."}


def get_sentence_translations(phrase):
    """Get translations for a given phrase and return a single dictionary."""
    # Ensure phrase is extracted correctly
    if isinstance(phrase, dict):
        phrase = phrase.get('phrase', '')  # Ensure to extract the correct key

    if not isinstance(phrase, str) or not phrase.strip():
        return {"phrase": phrase, "error": "Phrase must be a non-empty string."}

    words = phrase.split()
    translations_dict = {"phrase": phrase}

    for word in words:
        print(f"Translating word: '{word}'")
        word_translations = get_word_translations(word)
        if word_translations:
            translations_dict.update(word_translations)
        else:
            translations_dict[word] = "No translation found."

    return translations_dict
