from meilisearch import Client  
import os
from scribe_data.cli.db_utils.common_utils import get_word_translations, get_sentence_translations


# Retrieve the API key from environment variables
api_key = os.getenv("MEILISEARCH_API_KEY", None)  # Replace with the appropriate environment variable name
client = Client("http://localhost:7700", api_key=api_key)

def create_index():
    """Creates the MeiliSearch index for translations if it doesn't exist."""
    index_name = "translations_index"
    try:
        # Check if index already exists
        indexes = client.get_indexes()  # Get list of indexes
        if index_name not in [index['uid'] for index in indexes]:
            # Create the index without specific properties
            client.create_index(uid=index_name, options={"primaryKey": "id"})
            print(f"MeiliSearch index '{index_name}' created successfully.")
        else:
            print(f"MeiliSearch index '{index_name}' already exists.")
    except Exception as e:
        print(f"Error creating MeiliSearch index: {e}")

def add_documents():
    """Adds documents to the MeiliSearch index."""
    index_name = "translations_index"
    documents = [
        {
            "id": 1,
            "source_lang": "English",
            "phrase": "Hello",
            "french": "Bonjour",
            "spanish": "Hola",
            "portuguese": "Olá",
            "german": "Hallo"
        },
        {
            "id": 2,
            "source_lang": "English",
            "phrase": "Goodbye",
            "french": "Au revoir",
            "spanish": "Adiós",
            "portuguese": "Adeus",
            "german": "Auf Wiedersehen"
        },
        # Add more documents as needed
    ]
    try:
        client.index(index_name).add_documents(documents)
        print(f"Documents added to '{index_name}' successfully.")
    except Exception as e:
        print(f"Error adding documents to MeiliSearch: {e}")

def check_index_exists(index_name):
    """Checks if the specified MeiliSearch index exists."""
    try:
        indexes = client.get_indexes()  # Fetch all indexes
        exists = any(index['uid'] == index_name for index in indexes)
        if exists:
            print(f"Index '{index_name}' exists.")
            return True
        else:
            print(f"Index '{index_name}' does not exist.")
            return False
    except Exception as e:
        print(f"Error checking if index exists: {e}")
        return False