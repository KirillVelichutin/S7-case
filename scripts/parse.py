import json
import spacy
import re
import pandas as pd
from spacy.tokens import DocBin
from spacy.training import offsets_to_biluo_tags

from converter import convert_to_spacy


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

    return training_data 

def to_spacy(path, save_to):

    nlp = spacy.load('ru_core_news_sm')
    doc_bin = DocBin()
    
    with open(path, "r") as f:
        data = json.load(f)
    
    for item in data:
        doc = nlp.make_doc(item["text"])
        
        if "entities" in item:
            entities = []
            for start, end, label in item["entities"]:
                span = doc.char_span(start, end, label=label)
                if span is not None:
                    entities.append(span)
            doc.ents = entities
        
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


def prepare_data(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        lowertext = f.read().lower()
        data = json.loads(lowertext)
    
    
    train_ratio = 0.8
    split_index = int(len(data) * train_ratio)
    train_data = data[:split_index]
    val_data = data[split_index:]
    
    with open('../data/json_format/train_data.json', 'w', encoding='utf-8') as f:
        f.truncate(0)
        json.dump(train_data, f, ensure_ascii=False, indent=1, separators=(',', ': '))
    
    with open('../data/json_format/val_data.json', 'w', encoding='utf-8') as f:
        f.truncate(0)
        json.dump(val_data, f, ensure_ascii=False, indent=1, separators=(',', ': '))

    with open('../data/json_format/train_nofaulty.json', 'w') as f:
        f.truncate(0)
        json.dump(remove_faulty('../data/json_format/train_data.json'), f, ensure_ascii=False, indent=1, separators=(',', ': '))
    
    with open('../data/json_format/val_nofaulty.json', 'w') as f:
        f.truncate(0)
        json.dump(remove_faulty('../data/json_format/val_data.json'), f, ensure_ascii=False, indent=1, separators=(',', ': '))

    
    convert_to_spacy('../data/json_format/train_nofaulty.json', "train")
    convert_to_spacy('../data/json_format/val_nofaulty.json', "dev")


def find_passports(text):
    df = pd.read_csv('../data/passports_regions_data.csv')
    val_passport_codes = list(map(str, df['Код в серии паспорта РФ'].tolist()))

    df = pd.read_csv('../data/international_data.csv')
    val_international_codes = list(map(str, df['Код принадлежности документа'].tolist()))


    passports = []

    passport_pattern = r'\b(\d{2})[\s-]?(\d{2})[\s-]?(\d{6})\b'
    international_pattern = r'\b(\d{2})[-\s]?(\d{7})\b'

    for match in re.finditer(passport_pattern, text):
        raw = match.group()

        if raw[:2] in val_passport_codes:
            formatted = raw[:4] + ' ' + raw[4:]
            passports.append({
                "token": formatted,
                "tag": "PASSPORT",
            })

    for match in re.finditer(international_pattern, text):
        raw = match.group()

        if raw[:2] in val_international_codes:
            formatted = raw[:2] + ' ' + raw[2:]
            passports.append({
                "token": formatted,
                "tag": "INTERNATIONAL",
            })

    return passports

def find_emails(text):    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    
    emails = []
    
    for match in re.finditer(email_pattern, text):
        inst = match.group()
        
        ent_type = "EMAIL"
        
        emails.append({
            "token": inst,
            "tag": ent_type,
        })
            
    return emails

def find_phones(text):    
    phone_pattern = r'(?:\+?7|\b8)[\s\-()]?\d{3}[\s\-()]?\d{3}[\s\-()]?\d{2}[\s\-()]?\d{2}'
    
    phones = []
    
    for match in re.finditer(phone_pattern, text):
        raw_match = match.group()
        
        cleaned = raw_match.replace(' ', '')
        
        if cleaned.startswith('+7') or cleaned.startswith('8'):
            digits = cleaned[1:] if cleaned.startswith('+7') else cleaned
            if len(digits) == 11 and digits.isdigit():
                formatted = '+7 (' + digits[1:4] + ') ' + digits[4:7] + '-' + digits[7:9] + '-' + digits[9:11]
            else:
                formatted = cleaned
        else:
            formatted = cleaned

        ent_type = "PHONE"
        
        phones.append({
            "token": formatted,
            "tag": ent_type,
        })
    
    return phones

def find_iata(text):
    df = pd.read_csv('../data/airports_rus.csv')
    val_iata_codes = list(map(str, df['Код ИАТА'].tolist()))
    
    iatas = []
    
    iata_pattern = r'\b[A-Za-z]{3}\b'
    
    for match in re.finditer(iata_pattern, text):
        raw_code = match.group().upper()
        
        if raw_code in val_iata_codes:
            iatas.append({
                "token": raw_code,
                "tag": "IATA",
            })
    
    return iatas

def find_order_num(text):
    order_num_pattern = r'\b(?!S7)(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9]{6,7}\b'
    
    order_nums = []
    
    for match in re.finditer(order_num_pattern, text):
        raw_token = match.group()
        
        normalized_token = raw_token.upper()
        ent_type = "ORDER_NUMBER"
        
        order_nums.append({
            "token": normalized_token,
            "tag": ent_type,
        })
    
    return order_nums

def find_ticket_num(text):
    ticket_num_pattern = r'\b585\d{10}\b'
    
    ticket_nums = []
    
    for match in re.finditer(ticket_num_pattern, text):
        raw_token = match.group()
        
        normalized_token = raw_token.upper()
        ent_type = "TICKET_NUMBER"
        
        ticket_nums.append({
            "token": normalized_token,
            "tag": ent_type,
        })
    
    return ticket_nums

def find_flight(text):
    flight_pattern = r'\bS7\s?\d{1,4}\b'
    
    flights = []
    
    for match in re.finditer(flight_pattern, text):
        raw_match = match.group()
        
        normalized = "S7 " + raw_match[2:].replace(" ", "")
        ent_type = "FLIGHT"
        
        flights.append({
            "token": normalized,
            "tag": ent_type,
        })
    
    return flights
    

def process_request(user_message):
    text = re.sub(r'(\d)[\s*\-\(\)]+(?=\d)', r'\1', user_message)

    ents_data = []
    
    flights = find_flight(text)
    passports = find_passports(text)
    phones = find_phones(text)
    emails = find_emails(text)
    iatas = find_iata(text)
    ticket_nums = find_ticket_num(text)
    order_nums = find_order_num(text)
    
    if passports:
        for passport in passports:
            ents_data.append(passport)
    
    if phones:
        for phone in phones:
            ents_data.append(phone)
    
    if emails:
        for email in emails:
            ents_data.append(email)
            
    if iatas:
        for iata in iatas:
            ents_data.append(iata)
    
    if ticket_nums:
        for ticket_num in ticket_nums:
            ents_data.append(ticket_num)
            
    if flights:
        for flight in flights:
            ents_data.append(flight)
    
    if order_nums:
        for order_num in order_nums:
            if order_num["token"].lower() not in [data["token"] for data in ents_data]:
                ents_data.append(order_num)


    result = {
        "message": text,
        "tokens": ents_data
    }
    
    output = json.dumps(result, ensure_ascii=False, indent=2)
    return output

if __name__ == "__main__":
    user_message = user_message = "я вылетаю в париж 31 декабря S79520, меня зовут сёмин никита мой номер телефона +7 (285) 832-04-84. мой номер паспорта 40- 18 -295647 я вылетаю из домодедово в париж 64-7202067 aba 34C0Z0, 5854033941712 test123@mail.com"
    print(process_request(user_message))