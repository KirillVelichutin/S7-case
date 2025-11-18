import os
import random

from faker import Faker
import pandas as pd

from loc_generators import setup_faker_providers

TAGS = [
    'PHONE', 
    'PASSPORT', 
    'NAME', 
    'DOB', 
    'EMAIL', 
    'AIRPORT', 
    'CITY', 
    'COUNTRY', 
    'FLIGHT', 
    'TIME', 
    'DATE',  
    'INTERNATIONAL', 
    'TICKET_NUMBER', 
    'ORDER_NUMBER'
    ]

fake = Faker(locale='ru_RU')
fake = setup_faker_providers(fake)  # кастомные провайдеры
df = pd.read_csv(os.path.join('data', 'airports_rus.csv'))

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

PROMPT_KEYS = {
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
    'ORDER_NUMBER': 'номер бронирования или номер заказа - ORDER_NUMBER'
    }

PROMPT_CONTEXT = [
    lambda: random.choice(('Пользоавтели пишут неграмотно. ', 'Пользователи пишут грамотно. ')),
    lambda: random.choice(('Пользователи пишут грубо и используют ненормативную лексику. ', 'Пользователи пишут вежливо.' )),
    lambda: random.choice(('Сообщения состоят из нескольких предложений. ', 'Пользователи пишут в спешке. '))
]
