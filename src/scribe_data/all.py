import psycopg2
from elasticsearch import Elasticsearch, ElasticsearchException
from SPARQLWrapper import SPARQLWrapper, JSON

# Initialize Elasticsearch connection
es = Elasticsearch("http://localhost:9200")

def create_table():
    """Creates a PostgreSQL table for storing translations."""
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            database="scribe_data",
            user="your_username",
            password="your_password",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS translations (
            id SERIAL PRIMARY KEY,
            source_lang VARCHAR(2) NOT NULL,
            phrase TEXT NOT NULL,
            french TEXT,
            spanish TEXT,
            portuguese TEXT,
            german TEXT
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        print("Table 'translations' created successfully.")
    except psycopg2.Error as error:
        print("Database error occurred:", error.pgcode, error.pgerror)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def insert_translation(source_lang, phrase, translations):
    """Inserts a translation into PostgreSQL and indexes it in Elasticsearch."""
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            database="scribe_data",
            user="your_username",
            password="your_password",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO translations (source_lang, phrase, french, spanish, portuguese, german) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                source_lang,
                phrase,
                translations.get("fr", None),
                translations.get("es", None),
                translations.get("pt", None),
                translations.get("de", None)
            )
        )
        conn.commit()

        # Index the translation in Elasticsearch
        es.index(
            index="translations_index",
            body={
                "source_lang": source_lang,
                "phrase": phrase,
                **translations
            }
        )

        print(f"Translation for phrase '{phrase}' inserted and indexed successfully.")

    except (Exception, psycopg2.DatabaseError, ElasticsearchException) as error:
        print("Error while inserting translation:", error)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def search_translation(phrase):
    """Searches for a translation in Elasticsearch by the given phrase."""
    if not es:
        print("Elasticsearch connection not available.")
        return []

    try:
        response = es.search(index="translations_index", body={
            "query": {"match": {"phrase": phrase}}
        })
        return response['hits']['hits']
    except ElasticsearchException as e:
        print(f"Error searching for translation in Elasticsearch: {e}")
        return []

def get_translations(word):
    """Fetches translations from Wikidata for the specified word."""
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?translation ?languageCode
    WHERE {{
      ?lexeme dct:language wd:Q1860;  # English language
              wikibase:lemma "{word}";
              ontolex:sense/ontolex:translation ?senseTranslation.
      ?senseTranslation ontolex:representation ?translation;
                        dct:language ?language.
      ?language wdt:P218 ?languageCode.
      FILTER(?languageCode IN ("fr", "es", "pt", "de"))
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    translations = {result["languageCode"]["value"]: result["translation"]["value"]
                    for result in results["results"]["bindings"]}

    if translations:
        return translations
    else:
        return f"No translations found in Wikidata for '{word}'."

# Example usage
if __name__ == "__main__":
    create_table()
    example_word = "love"
    translations = get_translations(example_word)
    if translations:
        insert_translation("en", example_word, translations)
        search_results = search_translation(example_word)
        print("Search results:", search_results)
