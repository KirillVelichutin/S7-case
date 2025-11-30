import spacy
from spacy.tokens import DocBin
import json

def convert_to_spacy(data_path, data_type):
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Создаем пустую модель
    nlp = spacy.blank("ru")  # или "en" для английского
    doc_bin = DocBin()
    
    for i, item in enumerate(data):
        # Извлекаем текст и сущности
        text = item["text"]
        entities = item["entities"]
        
        # Создаем документ
        doc = nlp.make_doc(text)
        spacy_entities = []
        
        # Обрабатываем каждую сущность
        for entity in entities:
            start = entity[0]
            end = entity[1]
            label = entity[2]
            
            span = doc.char_span(
                start, 
                end, 
                label=label,
                alignment_mode="contract"  # важно для корректного выравнивания
            )
            spacy_entities.append(span)
        
        doc.ents = spacy_entities
        doc_bin.add(doc)
    
    
    doc_bin.to_disk(f"../data/spacy_format/{data_type}.spacy")