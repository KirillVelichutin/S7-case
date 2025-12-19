from fastapi import FastAPI
import spacy

app = FastAPI()
nlp = spacy.load('../models/model_1573983')

def extract_tags(input_text: str):
    doc = nlp(input_text)
    entities = []
    for ent in doc.ents:
        entities.append({ent.label_: ent.text})
    return entities

@app.post("/get_tags")
async def get_tags(text: str): 
    tags = extract_tags(text)
    return {"extracted_entities": tags}