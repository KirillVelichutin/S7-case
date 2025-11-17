from faker import Faker
import pandas as pd
from tqdm import tqdm
from rich import print as rprint

import random
import os
import json
from math import floor

from loc_generators import setup_faker_providers
from parse import jsonl_to_json, check_alignment, count_tags
#from context_gen import hf_api_completion
from screen_interractions import get_lines

fake = Faker(locale='ru_RU')
fake = setup_faker_providers(fake)  # добавляем кастомные провайдеры!
df = pd.read_csv(os.path.join('data', 'airports_rus.csv'))

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
    
    # marking out the message
    for key in tmp_entities:
        obj['entities'].append((obj['text'].find(key), obj['text'].find(key) + len(key), tmp_entities[key]))
    
    return obj

    
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
        'ORDER_NUMBER': 'номер бронирования или номер заказа - ORDER_NUMBER'}
    
    excluded_tags = []

    n_each = round(max(size / len(tags), 5))
    rel_batch = max(round(size / 100), 5)
    n_batch = rel_batch if rel_batch < 20 else 20
    
    total_tags_needed = len(tags) * n_each

    data = []
    last_percentage = 0

    print('\n'*2)
    with tqdm(total=100, colour="#2E271B", desc="generating data") as pbar:
        while len(excluded_tags) < len(set(tags)): # балансировка данных по тегам

            tag_combo = '' 
            rnd_iter = random.randint(0, round(len(tags.keys()) / 2))
            for _ in range(rnd_iter):
                while True:
                    new_tag = random.choice([key for key in list(tags.keys()) if key not in excluded_tags])
                    if new_tag not in tag_combo and new_tag not in excluded_tags:
                        tag_combo += tags[new_tag] + ', '
                        break
                    else:
                        break

            request = f'сгенерируй {n_batch} строк в формате JSONL (каждая строчка формата "message": "_СООБЩЕНИЕ_") сообщений пользователей боту-помощнику авиакомпании, в которых они пишут ему свои персональные данные. Замени персональные данные в сообщениях специальными строками: {tag_combo}. В каждом сообщении встречаются все перечесленные теги. Пользователи иногда пишут неграмотно, встречаются сообщения разной длины. Теги не встречаются без контекста - в сообщении всегда есть другие слова. Иногда, но редко, пользователи пишут грубо. Пользователи часто не здороваются, иногда печатают в спешкеСтарайся не повторять формулировки'
            
            lines = [line for line in get_lines(request, n_batch)]

            for obj in lines:
                try:
                    data.append(replaceAndLabel(obj['message']))
                except:
                    pass
            
            count = count_tags(dict=data)
            total = count['total_tags']

            current_percentage = min(round(total / (total_tags_needed / 100)), 100)
            pbar.update(current_percentage - last_percentage)
            last_percentage = current_percentage
            pbar.refresh()
            

            for tag in tags.keys():
                if tag in count.keys() and int(count[tag]) >= n_each:
                    if tag not in excluded_tags:
                        excluded_tags.append(tag)


    print(data[0:10])
    
    if export_file:
        try:
            with open(export_file, 'x') as f:
                json.dump(data, f, ensure_ascii=False, indent=1, separators=(',', ': '))
        except:

            with open(export_file, 'w', encoding='utf-8') as f:
                f.truncate(0)
                json.dump(data, f, ensure_ascii=False, indent=1, separators=(',', ': '))
    
    return data





if __name__ == '__main__':
    # print(fake.order_number())
    path = 'data/autodata2.json'
    print(generate_data(100, path))
    print(count_tags(path))
    #print(check_alignment(path)[2])
    # raw_data = []
    # with open('data/raw_data_kirill.json') as f:    
    #     file = json.load(f)
    #     for obj in file:
    #         raw_data.append({
    #             'message': obj['message']
    #         })

    # processed_data = []

    # for obj in raw_data:
    #     processed_data.append(replaceAndLabel(obj['message']))

    # with open('data/processed_kirill.json', 'w', encoding='utf-8') as f:
    #     f.truncate(0)
    #     json.dump(processed_data, f, ensure_ascii=False, indent=1, separators=(',', ': '))

    # # print(replaceAndLabel("Добрый день! Мой билет TICKET_NUMBER. Летим в COUNTRY. Дата рождения DOB."))
    # # print(fake.ticket_number())

    # print(count_tags('data/processed_kirill.json'))
    # check_alignment('data/processed_kirill.json')

