import os
import random

from faker import Faker
import pandas as pd


from loc_generators import setup_faker_providers, worded_time, worded_date
from get_datetime import parse_date, parse_time


TAGS = [
    'PHONE',
    'PASSPORT',
    'NAME',
    'EMAIL', 
    'AIRPORT', 
    'IATA',
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

def rnd_name():
    fake_name = fake.name().split()
    return random.choice((f'{fake_name[0]} {fake_name[1]}', f'{fake_name[1]} {fake_name[2]}', ' '.join(fake_name)))



DATAGEN = {
    'PHONE': lambda: fake.phone_number(),
    'PASSPORT': lambda: fake.passport_number(),
    'NAME': lambda: rnd_name(),
    'EMAIL': lambda: fake.email(),
    'AIRPORT': lambda: random.choices(df[['Название аэропорта']].dropna().reset_index(drop=True)['Название аэропорта'].tolist())[0], 
    'IATA': lambda: random.choices(df[['Код ИАТА']].dropna().reset_index(drop=True)['Код ИАТА'].tolist())[0],
    'FLIGHT': lambda: f"{random.choice(['SU', 'AF', 'LH', 'TK', 'BA', 'AY', 'S7', 'U6'])}{random.randint(100, 9999)}",
    'CITY': lambda: fake.city_name(),
    'TIME': lambda: random.choice((random.choice(':').join(fake.time().split(':')[0:2]), worded_time())),
    'DATE': lambda: random.choice((random.choice(' .').join(fake.date().split('-')[::-1]), random.choice(' .').join(fake.date().split('-')), worded_date())),
    'INTERNATIONAL': lambda: fake.international_passport(),
    'TICKET_NUMBER': lambda: fake.ticket_number(),
    'ORDER_NUMBER': lambda: fake.order_number(),
    'COUNTRY': lambda: fake.country(),
    }

STANDARD = {
    'PHONE': lambda token: ''.join([symbol for symbol in token if symbol in '1234567890+']),
    'NAME': lambda token: token.upper().split(),
    'DATE': lambda token: parse_date(token),
    'TIME': lambda token: parse_time(token), 
}

PROMPT_KEYS = {
    'PASSPORT': 'данные номера паспорта - PASSPORT', 
    'PHONE': 'данные номера телефона - PHONE', 
    'NAME': 'данные ФИО - NAME', 
    'EMAIL': 'адрес электронной почты - EMAIL', 
    'AIRPORT': 'название аэропорта - AIRPORT', 
    'IATA': 'код iata аэропорта - IATA', 
    'CITY': 'город - CITY', 
    'COUNTRY': 'страна - COUNTRY', 
    'FLIGHT': 'данные номера рейса - FLIGHT', 
    'DATE': 'данные о дате вылета или прилёта, или же данные о дате рождения - DATE', 
    'TIME': 'время - TIME', 
    'INTERNATIONAL': 'данные загранпаспорта - INTERNATIONAL', 
    'TICKET_NUMBER': 'данные номера билета - TICKET_NUMBER', 
    'ORDER_NUMBER': 'данные номера бронирования или номера заказа - ORDER_NUMBER'
    }

PROMPT_CONTEXT = [
    lambda: random.choices(('Пользоавтели пишут неграмотно. ', 'Пользователи пишут грамотно. '), weights=[40, 60])[0],
    lambda: random.choices(('Пользователи пишут грубо и используют ненормативную лексику. ', 'Пользователи пишут вежливо.' ), weights=[20, 80])[0],
    lambda: random.choice(('Сообщения состоят из нескольких предложений. ', 'Пользователи пишут в спешке. '))
    ]

ADDITIONAL = {
    'INTERNATIONAL': 'данные загранпаспорта - INTERNATIONAL', 
    'TIME': 'данные о времени - TIME',   
    'TICKET_NUMBER': 'данные номера билета - TICKET_NUMBER', 
}

TIME = [
        "я вылетаю в",
        "время вылета",
        "время прилёта",
        "рейс на",
        "время",
        "вылетаю ",
        "прилетаю",
        "приезжаю",
        "в",
        "часы прилёта",
        "часы вылета",
        "часяы прилёта и вылета",
        "лететь",
        "когда",
        "ёбаное время",
        "вот вам бля ваше время"
    ]

DATE = [
    "вылетаю",
    "вылет",
    "уезжаю",
    "прилетаю",
    "приезжаю",
    "прибываю",
    "рейс на",
    "рейс запланирован на",
    "число",
    "дата",
    "в числа",
    "на",
    "дата вылета",
    "время и дата",
    "удобная дата"
]

TOPIC = {
    "question1": [
        "пишу по поводу",
        "у меня есть вопрос про",
        "я хочу задать вопрос про",
        "непонятки с",
        "Нихера не понимаю по поводу",
        "Сука почему я ничего не знаю по поводу"
    ],
    "topic1": [
        "билета",
        "рейса",
        "багажа",
        "условий перевозки",
        "цены юилета",
        "времени полета",
        "регистрации на рейс",
        "пассажира",
    ],
    "question2": [
        "пишу про",
        "где",
        "где мой",
        "хочу спросить за",
        "хочу узнать про" 
    ],
    "topic2": [
        "билет",
        "рейс",
        "багаж",
        "условия перевозки",
        "цена билета",
        "время полета",
        "регистрацию на рейс",
        "пасажир"
    ]
}

TAIL = [
    "Это срочно.",
    "Это важно.",
    "Только давайте поскорее.",
    "Спасибо за помощь.",
    "Пожалуйста поторопитесь.",
    "Помогите.",
    "Только быстрее, уёбки!",
    "Если вы мне не поможете я больше никогда не буду летать вашей компанией",
    "Ужасный сервис!",
    "Спасибо за хороший сервис!",
    "Спасибо!"
]

HEAD = [
    "Здравствуйте!",
    "Здравствуйте",
    "помогите,",
    "пожалуйста,",
    "добрый день,",
    "добрый вечер,",
    "доброе утро,",
    "привет",
    "здарова",
    "хай",
    "Ёбаные вы твари!",
    "Подонки!",
]