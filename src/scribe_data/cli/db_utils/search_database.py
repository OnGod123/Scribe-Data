import os
from meilisearch import Client
from scribe_data.cli.db_utils.common_utils import get_word_translations, get_sentence_translations


# Retrieve the API key from environment variables
api_key = os.getenv("MEILISEARCH_API_KEY", None)
client = Client("http://localhost:7700", api_key=api_key)
def search_by_meilisearch(search_params):
    """Searches for translations in MeiliSearch based on the provided parameters."""
    if not client:
        print("MeiliSearch connection not available.")
        return None

    # Construct the search query based on the dictionary
    query = search_params.get('phrase', '')
    
    # Construct filters based on available languages
    filters = []
    if 'en' in search_params:
        filters.append(f"source_lang = '{search_params['en']}'")
    if 'fr' in search_params:
        filters.append(f"french = '{search_params['fr']}'")
    if 'es' in search_params:
        filters.append(f"spanish = '{search_params['es']}'")
    if 'pt' in search_params:
        filters.append(f"portuguese = '{search_params['pt']}'")
    if 'de' in search_params:
        filters.append(f"german = '{search_params['de']}'")

    # Combine filters into a single filter string
    filter_query = ' AND '.join(filters) if filters else None

    try:
        # Perform the search with the query and filters
        # If filter_query is None, simply omit the filter argument
        response = client.index("translations_index").search(query, filter=filter_query if filter_query else None)
        return response['hits'] if response['hits'] else None  # Return None if no results
    except Exception as e:
        print(f"Error searching for translation in MeiliSearch: {e}")
        return None

