import spacy

# Load English model
nlp = spacy.load("en_core_web_sm")


def extract_entities(text: str) -> dict:
    """
    Extracts named entities from user input.
    Returns dictionary with possible date, time, person, org.
    """

    doc = nlp(text)

    entities = {
        "date": [],
        "time": [],
        "person": [],
        "organization": []
    }

    for ent in doc.ents:
        if ent.label_ == "DATE":
            entities["date"].append(ent.text)

        elif ent.label_ == "TIME":
            entities["time"].append(ent.text)

        elif ent.label_ == "PERSON":
            entities["person"].append(ent.text)

        elif ent.label_ == "ORG":
            entities["organization"].append(ent.text)

    return entities
