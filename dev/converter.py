import spacy
from spacy.tokens import DocBin
import json


def convert_to_spacy_with_lemmatization(data_path, data_type):
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    nlp = spacy.load("ru_core_news_sm")
    doc_bin = DocBin()

    for i, item in enumerate(data):
        text = item["text"]
        entities = item["entities"]

        original_doc = nlp(text)

        lemmatized_tokens = []
        token_start_positions = []
        current_pos = 0

        for token in original_doc:
            token_start_positions.append(current_pos)
            lemmatized_token = token.lemma_
            lemmatized_tokens.append(lemmatized_token)
            current_pos += len(lemmatized_token) + 1

        lemmatized_text = " ".join(lemmatized_tokens)

        doc = nlp.make_doc(lemmatized_text)

        spacy_entities = []

        for entity in entities:
            original_start = entity[0]
            original_end = entity[1]
            label = entity[2]

            entity_start_token = None
            entity_end_token = None

            for token_idx, token in enumerate(original_doc):
                token_start = token.idx
                token_end = token.idx + len(token.text)
                
                if token_start <= original_start < token_end:
                    entity_start_token = token_idx
                if token_start < original_end <= token_end:
                    entity_end_token = token_idx
                    break

            if entity_start_token is not None and entity_end_token is not None:
                new_start = token_start_positions[entity_start_token]
                
                last_token_in_entity = original_doc[entity_end_token]
                last_lemmatized_len = len(last_token_in_entity.lemma_)
                new_end = token_start_positions[entity_end_token] + last_lemmatized_len

                if 0 <= new_start < new_end <= len(lemmatized_text):
                    span = doc.char_span(
                        new_start,
                        new_end,
                        label=label,
                        alignment_mode="contract"
                    )
                    if span is not None:
                        spacy_entities.append(span)

        doc.ents = spacy_entities
        doc_bin.add(doc)

    doc_bin.to_disk(f"../data/spacy_format/{data_type}.spacy")


def convert_to_spacy(data_path, data_type):
    convert_to_spacy_with_lemmatization(data_path, data_type)