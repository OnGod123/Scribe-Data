import os
from meilisearch import Client as MeiliClient
import psycopg2

# Initialize MeiliSearch client using environment variable for the API key
meili_client = MeiliClient(
    "http://localhost:7700",
    api_key=os.getenv("MEILISEARCH_API_KEY")
)

def insert_translation(source_lang, phrase, translations):
    """Inserts a translation into PostgreSQL and indexes it in MeiliSearch."""
    conn = None
    cur = None
    try:
        # Connect to PostgreSQL using environment variables
        conn = psycopg2.connect(
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT")
        )
        cur = conn.cursor()

        # Insert into PostgreSQL
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

        # Index the translation in MeiliSearch
        meili_client.index("translations_index").add_documents([
            {
                "id": cur.lastrowid,  # Use the last inserted ID from PostgreSQL
                "source_lang": source_lang,
                "phrase": phrase,
                **translations
            }
        ])

        print(f"Translation for phrase '{phrase}' inserted into PostgreSQL and indexed in MeiliSearch successfully.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while inserting translation:", error)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
