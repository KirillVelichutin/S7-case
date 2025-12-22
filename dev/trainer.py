import spacy
from spacy.tokens import DocBin
from spacy.tokens import SpanGroup
from spacy.cli.train import train

from thinc.api import require_gpu

from pathlib import Path
import json


def make_snapcat(json_path, export_path):
    nlp = spacy.blank("ru")
    with open(json_path, 'r') as f:
        loaded = json.load(f)

    db = DocBin()

    for item in loaded:
        text = item["text"]

        doc = nlp.make_doc(text)

        spans = []
        for start_char, end_char, label in item["entities"]:
            span = doc.char_span(start_char, end_char, label=label)

            if span is None:
                print(f"Warning: Could not create span for text '{text[start_char:end_char]}'")
                print(f"  Character positions: {start_char}-{end_char}")
                print(f"  Text at that position: '{text[start_char:end_char]}'")

                if text[start_char:end_char] in text:
                    actual_start = text.find(text[start_char:end_char])
                    if actual_start != -1:
                        span = doc.char_span(actual_start, actual_start + (end_char - start_char), label=label)
                        print(f"  Fixed: Using positions {actual_start}-{actual_start + (end_char - start_char)}")

            if span:
                spans.append(span)

    group = SpanGroup(doc, name="sc", spans=spans)
    doc.set_ents(spans)
    doc.spans["sc"] = group
    db.add(doc)


    db.to_disk(export_path)
    print(f"\nCreated training data with {len(db)} documents")


def training(config_path, output_dir, train_path, dev_path, model):
    doc_bin = DocBin().from_disk(train_path)
    
    
    if model == "null":
        nlp = spacy.blank("ru")
        print("=== new model created ===")
    else:
        nlp = spacy.load(f"{model}")
        print(f"=== loaded: {model} ===")


    doc_bin = DocBin().from_disk(f"{train_path}")
    docs = list(doc_bin.get_docs(nlp.vocab))

    total_tokens = sum(len(doc) for doc in docs)
    print(f"* Tokens: {total_tokens}")

    
    batch_size = 2000
    eval_freq = 10
    max_epochs = 150
    drop = 0.1
    learn_rate = 0.001
    
    num_entities = 0
    entity_counts_by_label = {}

    for doc in doc_bin.get_docs(nlp.vocab):
        num_entities += len(doc.ents)
        for ent in doc.ents:
            label = ent.label_
            entity_counts_by_label[label] = entity_counts_by_label.get(label, 0) + 1
    
    
    max_entity_counts = max(entity_counts_by_label.values())
    
    print(f"* Entities: {num_entities}")
    print(f"* Max entity counts per label: {max_entity_counts}")
    print(f"* Batch size: {batch_size}")        
    print(f"* Max epochs: {max_epochs}")
    print(f"* Dropout: {drop}")
    # print(f"* Learn rate: {learn_rate}")
    print(f"* Eval freq: {eval_freq}")


    print("=== Training starts ===")


    config_path = Path(f"{config_path}")
    output_path = Path(f"{output_dir}")
    train_path = Path(f"{train_path}")
    dev_path = Path(f"{dev_path}")

    train(
        config_path=config_path,
        output_path=output_path,
        overrides={
            "paths.train": str(train_path),
            "paths.dev": str(dev_path),
            "training.seed": 42,
            "corpora.dev.path": "${paths.dev}",
            "corpora.train.path": "${paths.train}",
            "nlp.batch_size": batch_size,
            "training.max_epochs": max_epochs,
            "training.dropout": drop,
            # "training.optimizer.learn_rate": learn_rate,
            "training.max_steps": 20000,
            "training.eval_frequency": eval_freq,
            "training.logger.@loggers": "spacy.ConsoleLogger.v3",
            "training.logger.progress_bar": "eval",
            "training.logger.console_output": "true",
            "training.logger.output_file": "../analysis/training_history/training_history.jsonl"
        },
        use_gpu=0,
    )



if __name__ == '__main__':
    if require_gpu(0):
        print("spaCy успешно использует GPU")
    else:
        print("GPU недоступен для spaCy")
        
    gpu = spacy.prefer_gpu()
    print(gpu)


    
    # train_path = "../data/json_format/train_nofaulty.json"
    # val_path = "../data/json_format/val_nofaulty.json"
    spanpath = "../data/spacy_format/spans.spacy"
    validpath = "../data/spacy_format/dev.spacy"
    
    # make_snapcat(train_path, spanpath)
    # make_snapcat(val_path, validpath)
    
    # prepare_data("../data/initial_data/composit3.json")
    
    config_path = "../models/config.cfg"
    output_dir = "../models"
    # train_path = "../data/spacy_format/train.spacy"
    # dev_path = "../data/spacy_format/dev.spacy"
    
    model = "ru_core_news_sm"
    
    training(
            config_path,
            output_dir,
            spanpath,
            validpath,
            model
            )
    