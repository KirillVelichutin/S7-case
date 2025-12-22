import json

import spacy
from spacy.tokens import DocBin
from spacy.training import offsets_to_biluo_tags
from spacy.tokens import DocBin, SpanGroup

nlp = spacy.load("ru_core_news_sm")
def transmute(dict, key):
    new_dict = {key: []}
    
    try:
        for item in dict[key]:
            new_dict[key].append((item[0], item[1], item[2]))
    except:
        print('incorrect data format')

    return new_dict

def examples(path):

    with open(path, 'r') as f:
        data = json.load(f)
        training_data = []

        for item in data:
            text = item['text']
            entities = transmute(item, 'entities')
            training_data.append((text, entities))

    return training_data # [(text, {'entities': [()]})]
                         # to use as spacy Example: examples = [Example.from_dict(nlp.make_doc(text), example) for text, example in data]

def to_spacy(path, save_to):

    doc_bin = DocBin()
    
    with open(path, "r") as f:
        data = json.load(f)
    
    for item in data:
        doc = nlp.make_doc(item["text"])
        
        # Add entities
        if "entities" in item:
            entities = []
            for start, end, label in item["entities"]:
                span = doc.char_span(start, end, label=label)
                if span is not None:
                    entities.append(span)
            doc.ents = entities
        
        # Add categories
        if "cats" in item:
            doc.cats = item["cats"]
        
        doc_bin.add(doc)
    
    doc_bin.to_disk(save_to)
    print(f"Converted {len(data)} documents to {save_to}")

def jsonl_to_json(path):
    with open(path) as f:
        lines = f.read().split('\n')
        obj = [json.loads(line) for line in lines]
    return obj

def check_alignment(path, verbose=True):
    with open(path) as f:
        file = json.load(f)
        total_misalligned = 0
        data = []
        for obj in file:
            text = obj['text']

            entities = obj['entities']
            doc = nlp.make_doc(text)
            ent_data = []
            for start, end, label in entities:
                entity_text = text[start:end]
                tokens_in_entity = []
                for token in doc:
                    if start <= token.idx < end:
                        tokens_in_entity.append(token.text)
                ent_data.append({
                    'text': entity_text,
                    'label': label,
                    'coords': f'{start}-{end}',
                    'tokens': tokens_in_entity
                })

            
            bilou_tags = offsets_to_biluo_tags(doc, entities)
            total_misalligned += bilou_tags.count('-')
            data.append({
                'text': text,
                'ent_data': ent_data, 
                'bilou_tags': bilou_tags,
                'misaligned': f'{bilou_tags.count("-")}'
            })

        faulty = 0
        for item in data:
            if item['misaligned'] != '0':
                if verbose:
                    print(f'"{item["text"]}"')
                    print(f'entities: {item["ent_data"]}')
                    print(f'bilou tags: {item["bilou_tags"]}')
                    print(f'misaligned: {item["misaligned"]}')
                    print('---')
                faulty += 1
        ratio = round(faulty / (len(data)/100))
        if verbose:
            print(f'\nTOTAL MISALLIGNED: {total_misalligned}\nTOTAL FAULTY EXAMPLES: {faulty}\nFAULTY PERCENTAGE: {ratio}%')
    
    return data, total_misalligned, faulty

def count_tags(path=None, dict=None):
    data = []
    if path:
        with open(path) as f:    
            data = json.load(f)
    elif dict:
        data = dict

    tags = []
    for obj in data:
        for ent in obj['entities']:
            tags.append(ent[2])

    tag_data = {}
    for tag in set(tags):
        tag_data[tag] =  tags.count(tag)

    total_tags = 0
    for key in tag_data.keys():
        total_tags += tag_data[key]
    
    tag_data['total_strings'] = len(data)
    tag_data['total_tags'] = total_tags
    
    return tag_data

def remove_faulty(path):
    data, total, faulty_str = check_alignment(path, verbose=False)
    faulty_messages = []
    for item in data:
        if item['misaligned'] != '0':
            faulty_messages.append(item['text'])

    with open(path) as f:
        nofaulty = []
        for obj in json.load(f):
            if obj['text'] not in faulty_messages:
                nofaulty.append(obj)

    return nofaulty


def to_spacy(path, save_to):

    doc_bin = DocBin()
    
    with open(path, "r") as f:
        data = json.load(f)
    
    for item in data:
        doc = nlp.make_doc(item["text"])
        
        # Add entities
        if "entities" in item:
            entities = []
            for start, end, label in item["entities"]:
                span = doc.char_span(start, end, label=label)
                if span is not None:
                    entities.append(span)
            doc.ents = entities
        
        # Add categories
        if "cats" in item:
            doc.cats = item["cats"]
        
        doc_bin.add(doc)
    
    doc_bin.to_disk(save_to)
    print(f"Converted {len(data)} documents to {save_to}")

    return doc_bin

# raw_path = "./data/doublespans1.json"
# train_path = "./data/train.json"
# val_path = "./data/val.json"
# spanpath = "./data/spans.spacy"
# validpath = "./data/dev.spacy"

# with open(raw_path, "r") as f:
#     lowerdata = f.read().lower()
#     loaded = json.loads(lowerdata)
#     random.shuffle(loaded)
#     size = floor(len(loaded) / 5)
#     train = loaded[0:size*4]
#     val = loaded[size*4:]

# with open(train_path, 'w') as f:
#     json.dump(train, f, ensure_ascii=False, indent=1, separators=(',', ': '))

# with open(val_path, 'w') as f:
#     json.dump(val, f, ensure_ascii=False, indent=1, separators=(',', ': '))


def make_snapcat(json_path, export_path):
    # Create blank model
    nlp = spacy.blank("ru")
    with open(json_path, 'r') as f:
        loaded = json.load(f)

    # Convert to .spacy format for SpanCat
    db = DocBin()

    for item in loaded:
        text = item["text"]
        
        # Step 1: Create a document from text
        doc = nlp.make_doc(text)  # Tokenization happens here
        
        # Step 2: Convert character spans to token spans using char_span
        spans = []
        print(item["entities"])
        if not len(item["entities"]) == 0:
            for start_char, end_char, label in item["entities"]:
                # char_span converts character positions to token indices
                span = doc.char_span(start_char, end_char, label=label)

                if span is None:
                    # Common issue: character offsets don't align with tokens
                    print(f"Warning: Could not create span for text '{text[start_char:end_char]}'")
                    print(f"  Character positions: {start_char}-{end_char}")
                    print(f"  Text at that position: '{text[start_char:end_char]}'")
                    
                    # Try to fix by finding the text in the document
                    if text[start_char:end_char] in text:
                        # Find where this text actually appears
                        actual_start = text.find(text[start_char:end_char])
                        if actual_start != -1:
                            span = doc.char_span(actual_start, actual_start + (end_char - start_char), label=label)
                            print(f"  Fixed: Using positions {actual_start}-{actual_start + (end_char - start_char)}")
                
            if span:
                spans.append(span)
                # print(f"Successfully created span: '{span.text}' → {label}")
        
        # Step 3: Store spans in doc.spans (REQUIRED for SpanCat)
        # Use key "sc" (default for SpanCat) or choose your own
        group = SpanGroup(doc, name="sc", spans=spans)
        doc.set_ents(spans)
        doc.spans["sc"] = group
        db.add(doc)


    # Save
    db.to_disk(export_path)
    print(f"\nCreated training data with {len(db)} documents")


    

