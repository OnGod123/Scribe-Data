from SPARQLWrapper import SPARQLWrapper, JSON

def get_translations(word):
    # Define the SPARQL endpoint for Wikidata
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    
    # SPARQL query to find the lexeme in multiple languages
    query = f"""
    SELECT ?translation ?languageCode
    WHERE {{
      ?lexeme dct:language wd:Q1860;                 # English language
              wikibase:lemma "{word}";               # Lemma of the word in English
              ontolex:sense/ontolex:translation ?senseTranslation.  # Link to translations
              
      ?senseTranslation ontolex:representation ?translation; 
                        dct:language ?language.
                        
      ?language wdt:P218 ?languageCode.              # Language code like 'fr', 'es', 'pt'
      
      FILTER(?languageCode IN ("fr", "es", "pt"))    # Limit to French, Spanish, and Portuguese
    }}
    """
    
    # Set the query and return format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute the query and process results
    results = sparql.query().convert()
    
    # Process results into a dictionary
    translations = {result["languageCode"]["value"]: result["translation"]["value"]
                    for result in results["results"]["bindings"]}
    
    # Return translations or message if not found
    if translations:
        return translations
    else:
        return f"The word '{word}' was not found in Wikidata for the specified languages."

# Example usage
word_to_translate = "love"
print(get_translations(word_to_translate))
