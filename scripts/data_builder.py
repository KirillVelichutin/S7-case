from faker import Faker
import pandas as pd
import random
import os
import json

from loc_generators import setup_faker_providers
#from context_gen import hf_api_completion

from reader import read_data
from parse import remove_faulty
from converter import convert_to_spacy

fake = Faker(locale='ru_RU')
fake = setup_faker_providers(fake)  # добавляем кастомные провайдеры!
df = pd.read_csv(os.path.join('../data', 'airports_rus.csv'))

TAGS = ['PHONE', 'PASSPORT', 'NAME', 'DOB', 'EMAIL', 'AIRPORT', 'CITY', 'COUNTRY', 'FLIGHT', 'TIME', 'DATE',  'INTERNATIONAL', 'TICKET_NUMBER', 'ORDER_NUMBER']

DATAGEN = {
    'PHONE': lambda: fake.phone_number(),
    'PASSPORT': lambda: fake.passport_number(),
    'NAME': lambda: fake.name(),
    'DOB': lambda: fake.date_of_birth(),
    'EMAIL': lambda: fake.email(),
    'AIRPORT': lambda: random.choice(df[random.choice(['Название аэропорта', 'Код ИАТА'])].dropna().reset_index(drop=True)), 
    'FLIGHT': lambda: f"{random.choice(['SU', 'AF', 'LH', 'TK', 'BA', 'AY', 'S7', 'U6'])}{random.randint(100, 9999)}",
    'CITY': lambda: fake.city_name(),
    'TIME': lambda: fake.time(),
    'DATE': lambda: fake.date(),
    'INTERNATIONAL': lambda: fake.international_passport(),
    'TICKET_NUMBER': lambda: fake.ticket_number(),
    'ORDER_NUMBER': lambda: fake.order_number(),
    'COUNTRY': lambda: fake.country()
    #'BOOKING_REF': lambda: fake.booking_ref(),
    #'BOARDING_PASS': lambda: fake.boarding_pass(),
    #'EMD_NUMBER': lambda: fake.emd_number(),
    #'TICKET': lambda: ''.join([str(random.randint(0, 9)) for _ in range(13)]),
    #'BIRTH_CERTIFICATE': lambda: fake.birth_certificate(),
    #'VISA': lambda: fake.visa(),
    
}

def replaceAndLabel(message):
    
    global TAGS, DATAGEN

    obj = {
        'text': message,
        'entities': []
    }

    tmp_entities = {}

    # inserting generated data
    for tag in TAGS:

        if tag in message:
            split_message = [part for part in obj['text'].split(tag)]
            augmented_message = ''
            
            for i in range(len(split_message) - 1):
                rnd_data = str(DATAGEN[tag]())
                tmp_entities[rnd_data] = tag
                augmented_message += f'{split_message[i]}{rnd_data}'
                
                if i == len(split_message) - 2:
                    augmented_message += split_message[i + 1]
            if len(augmented_message) < 2:
                augmented_message = f'ERROR: {obj['text']}'
            obj['text'] = augmented_message
    
    for key in tmp_entities:
        obj['entities'].append((obj['text'].find(key), obj['text'].find(key) + len(key), tmp_entities[key]))
    
    return obj

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
    
    return tag_data
    
def generate_data(size, export_file=None):

    tags = {
        'PASSPORT': 'номер паспорта - PASSPORT', 
        'PHONE': 'номер телефона - PHONE', 
        'NAME': 'ФИО - NAME', 
        'EMAIL': 'электронная почта - EMAIL', 
        'DOB': 'дата рождения - DOB', 
        'AIRPORT': 'название или код аэропорта - AIRPORT', 
        'CITY': 'город - CITY', 
        'COUNTRY': 'страна - COUNTRY', 
        'FLIGHT': 'номер рейса - FLIGHT', 
        'DATE': 'дата - DATE', 
        'TIME': 'время - TIME', 
        'INTERNATIONAL': 'загранпаспорт - INTERNATIONAL', 
        'TICKET_NUMBER': 'номер билета - TICKET_NUMBER', 
        'ORDER_NIMBER': 'номер бронирования или номер заказа - ORDER_NUMBER'}
    
    excluded_tags = []

    n_each = round(size / len(tags))
    n_batch = max(round(size / 100), 10)

    data = []

    while len(excluded_tags) < len(tags): # балансировка данных по тегам

        tag_combo = ''
        for _ in range(random.randint(0, round(len(tags.keys()) / 2))):
            flag = True
            while flag:
                new_tag = random.choice(list(tags.keys()))
                print(new_tag, new_tag in excluded_tags)
                if new_tag not in tag_combo and new_tag not in excluded_tags:
                    tag_combo += tags[new_tag] + ', '
                    flag = False

        print(tag_combo)

        request = f'сгенерируй {n_batch} строк в формате JSONL (каждая строчка формата "message": "_СООБЩЕНИЕ_") сообщений пользователей боту-помощнику авиакомпании, в которых они пишут ему свои персональные данные. Замени персональные данные в сообщениях специальными строками: {tag_combo}. В каждом сообщении встречаются все перечесленные теги. Пользователи иногда пишут неграмотно, встречаются сообщения разной длины. Теги не встречаются без контекста - в сообщении всегда есть другие слова. Иногда, но редко, пользователи пишут грубо. Пользователи часто не здороваются, иногда печатают в спешкеСтарайся не повторять формулировки'
        print('\nwaiting for response...\n')
        lines = [json.loads(line) for line in hf_api_completion(request)]

        print(lines[0:10])

        for obj in lines:
            data.append(replaceAndLabel(obj['message']))
        
        count = count_tags(dict=data)
        print(count)
        for tag in tags.keys():
            if tag in count.keys() and int(count[tag]) > n_each:
                if tag not in excluded_tags:
                    excluded_tags.append(tag)
                    print(f'excluded {tag}')

        print(len(tags), len(excluded_tags), excluded_tags)

    print(data[0:10])
    
    if export_file:
        json.load(data)
        try:
            with open(export_file, 'x') as f:
                json.dump(data, f, ensure_ascii=False, indent=1, separators=(',', ': '))
        except:

            with open(export_file, 'w', encoding='utf-8') as f:
                f.truncate(0)
                json.dump(data, f, ensure_ascii=False, indent=1, separators=(',', ': '))
    
    return data




if __name__ == '__main__':
    raw_data_path = "../data/initial_data/data.csv"
    raw_data = read_data(raw_data_path)
    
    processed_data = []

    for obj in raw_data:
        processed_data.append(replaceAndLabel(obj['message']))
        
    
    with open('../data/json_format/processed_data.json', 'w', encoding='utf-8-sig') as f:
        f.truncate(0)
        json.dump(processed_data, f, ensure_ascii=False, indent=1, separators=(',', ': '))