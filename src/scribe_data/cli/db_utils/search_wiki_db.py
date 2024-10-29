from SPARQLWrapper import SPARQLWrapper, JSON
import socket
import argparse

def check_internet_connection():
    """Check if there is an internet connection."""
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
    
    print("SPARQL Query:")
    print(query)

    if not check_internet_connection():
        print("No internet connection. Please check your network settings.")
        return None

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        print(f"SPARQL results: {results}")
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

def get_word_translations(word):
    """Get translations for a single word and return a dictionary."""
    target_languages = ['fr', 'es', 'de', 'pt']  # Specify the target languages here
    translations = get_translations_for_word(word, target_languages)

    if translations:
        return {word: translations}
    else:
        return {word: f"No translations found for '{word}'."}

def get_sentence_translations(phrase):
    """Get translations for a given phrase and return a dictionary."""
    words = phrase.split()
    translations_dict = {"phrase": phrase}

    for word in words:
        print(f"Translating word: {word}")
        word_translations = get_word_translations(word)
        translations_dict.update(word_translations)

    return translations_dict