DEFINITION_PROMPT = """
Analyze the given word and provide a clear definition and an example sentence for the word {word}.
If the word appears to be misspelled, DO NOT attempt to guess what it might be. return the FORMAT GIVEN BELOW.
{{
    "error": "Word not found",
    "details": "The word '{word}' appears to be misspelled or invalid."
}}
If word is valid then format your response as a JSON object with the following structure:
{{
    "word": "{word}",
    "definition": "The definition of the word",
    "example": "An example sentence using the word"
}}

"""