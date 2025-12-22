import random
import re

from faker.providers import BaseProvider
from faker_airtravel import AirTravelProvider

class RussianDocumentsProvider(BaseProvider):
    """Провайдер для российских документов"""
    
    def international_passport(self):
        """Генерация номера загранпаспорта"""
        series = random.choice(['53', '60', '61', '62', '63', '64', '65', '70', '71', '72'])
        number = f"{self.random_int(1000000, 9999999)}"
        
        formats = [
            f"{series} {number}",           # 65 1234567
            f"{series}{number}",            # 651234567
            f"{series}-{number}"            # 65-1234567
        ]
        return random.choice(formats)
    
    def birth_certificate(self):
        """Генерация номера свидетельства о рождении"""
        roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
        letters = ['ЕР', 'МС', 'АВ', 'СР', 'ТУ', 'НР', 'КЕ', 'МР']
        number = f"{self.random_int(100000, 999999)}"
        
        formats = [
            f"{random.choice(roman_numerals)}-{random.choice(letters)} № {number}", # II-ЕР № 123456
            f"{random.choice(roman_numerals)}-{random.choice(letters)} {number}",   # II-ЕР 123456
            f"{random.choice(roman_numerals)}-{random.choice(letters)}№{number}",   # II-ЕР№123456
            f"{random.choice(roman_numerals)}-{random.choice(letters)}.№{number}",  # II-ЕР.№123456
            f"свидетельство {random.choice(roman_numerals)}-{random.choice(letters)} № {number}" # с текстом
        ]
        return random.choice(formats)
    
    def visa(self):
        """Генерация номера визы"""
        # Шенгенская виза
        if random.random() > 0.5:
            chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            visa_number = ''.join(random.choices(chars, k=9))
            formats = [
                visa_number,
                f"{visa_number[:3]} {visa_number[3:6]} {visa_number[6:]}",  # A12 345 67B
                f"{visa_number[:3]}-{visa_number[3:6]}-{visa_number[6:]}",  # A12-345-67B
                f"виза № {visa_number}"
            ]
        else:
            # Американская/другие визы
            visa_number = f"{self.random_int(10000000, 99999999)}"
            formats = [visa_number, f"виза № {visa_number}"]
        
        return random.choice(formats)

class AviationDocumentsProvider(BaseProvider):
    """Провайдер для авиационных документов"""
    
    def ticket_number(self):
        """Генерация номера авиабилета"""
        airline_codes = ['421', '555', '262', '124'] #  S7, SU, U6, AC
        airline = random.choice(airline_codes)
        number = f"{self.random_int(1000000000, 9999999999)}"

        return f"{airline}{number}"
    
    def booking_ref(self):
        """Генерация номера бронирования (PNR)"""
        chars = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'  # без I, O, Q
        pnr = ''.join(random.choices(chars, k=6))
        
        formats = [
            pnr,
            f"{pnr[:3]}-{pnr[3:]}",        # ABC-123
            f"бронь {pnr}",                 # бронь ABC123
            f"PNR {pnr}",                   # PNR ABC123
            f"код {pnr}",                   # код ABC123
            f"номер брони {pnr}",
            f"бронирование {pnr}"
        ]
        return random.choice(formats)
    
    def boarding_pass(self): # Нужен ли?
        """Генерация номера посадочного талона""" 
        # 50% chance что будет как PNR, 50% - отдельный номер
        if random.random() > 0.5:
            return self.booking_ref()
        else:
            number = f"{self.random_int(1000000000, 9999999999999)}"
            formats = [
                number,
                f"посадочный {number}",
                f"талон {number}",
                f"BP{number}",              # Boarding Pass
                f"посадочный талон {number}"
            ]
            return random.choice(formats)
    
    def emd_number(self): # Нужен ли?
        """Генерация номера EMD (Electronic Miscellaneous Document)"""
        airline_codes = ['421'] #, '555', '262']
        airline = random.choice(airline_codes)
        number = f"{self.random_int(1000000000, 9999999999)}"
        
        formats = [
            f"{airline} {number}",          # 421 1234567890
            f"EMD {airline} {number}",      # EMD 421 1234567890
            f"{airline}{number}",           # 4211234567890
            f"документ EMD {airline} {number}",
            f"номер EMD {airline} {number}"
        ]
        return random.choice(formats)
    
    def order_number(self):
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'  # только заглавные буквы и цифры
    
        # Генерируем строку из 7 случайных символов
        random_chars = ''.join(random.choices(characters, k=7))
        
        formats = [
            random_chars,                                      # DRE5TW6
            f"ORD{random_chars}",                             # ORDDRE5TW6
            #f"ORDER-{random_chars}",                          # ORDER-DRE5TW6
            #f"ЗАКАЗ{random_chars}",                           # ЗАКАЗDRE5TW6
            #f"№{random_chars}",                               # №DRE5TW6
            #f"заказ №{random_chars}",                         # заказ №DRE5TW6
            f"{random_chars[:3]}-{random_chars[3:]}",         # DRE-5TW6
            f"{random_chars[:2]}{random_chars[2:4]}{random_chars[4:]}",  # DR E5 TW6 (без пробелов)
        ]
        return random.choice(formats)

class RussianAviationProvider(BaseProvider):
    """Комплексный провайдер для российских авиационных данных"""
    
    def __init__(self, generator):
        super().__init__(generator)
        self.documents_provider = RussianDocumentsProvider(generator)
        self.aviation_provider = AviationDocumentsProvider(generator)
    
    def russian_airline(self):
        """Российские авиакомпании"""
        airlines = ['S7 Airlines', 'Аэрофлот', 'Уральские авиалинии', 'Победа', 'Ютейр', 'Россия']
        return random.choice(airlines)
    
    # def russian_airport_iata(self):
    #     """Российские аэропорты с кодами IATA"""
    #     airports = ['SVO', 'DME', 'VKO', 'LED', 'KRR', 'OVB', 'KJA', 'AER', 'ROV', 'KGD', 'MRV', 'GOJ']
    #     return random.choice(airports)
    
    def russian_flight_number(self):
        """Номера рейсов российских авиакомпаний"""
        airlines = ['S7', 'SU', 'U6', 'DP', '5N', 'WZ', 'FV']
        airline = random.choice(airlines)
        number = self.random_int(1, 9999)
        return f"{airline}{number}"
    
    # Делегирование методов документов для удобства
    def international_passport(self):
        return self.documents_provider.international_passport()
    
    def birth_certificate(self):
        return self.documents_provider.birth_certificate()
    
    def visa(self):
        return self.documents_provider.visa()
    
    def ticket_number(self):
        return self.aviation_provider.ticket_number()
    
    def booking_ref(self):
        return self.aviation_provider.booking_ref()
    
    def boarding_pass(self):
        return self.aviation_provider.boarding_pass()
    
    def emd_number(self):
        return self.aviation_provider.emd_number()
    
    def order_number(self):
        return self.aviation_provider.order_number()

# Утилиты для удобного импорта
def setup_faker_providers(faker_instance):
    """Настройка всех провайдеров для Faker instance"""
    faker_instance.add_provider(AirTravelProvider)
    faker_instance.add_provider(RussianAviationProvider)
    return faker_instance

def get_all_document_types():
    """Возвращает список всех типов документов"""
    return [
        'INTERNATIONAL_PASSPORT', 
        'BIRTH_CERTIFICATE',
        'VISA',
        'TICKET_NUMBER',
        'BOOKING_REF',
        'BOARDING_PASS',
        'EMD_NUMBER',
        'ORDER_NUMBER'
    ]

HOURS = [
    "час",
    "два",
    "три",
    "четыре",
    "пять",
    "шесть",
    "семь",
    "восемь",
    "девять",
    "десять",
    "одиннадцать",
    "двенадцать",
    "тринадцать",
    "четырнадцать",
    "пятнадцать",
    "шестнадцать",
    "семнадцать",
    "восемнадцать",
    "девятнадцать",
    "двадцать",
    "двадцать один",
    "двадцать два",
    "двадцать три"
]

MINUTES = [
    "пятнадцать",
    "тридцать",
    "сорок",
    "пятьдесят",
    "сорок пять",
    "двадцать",
    "двадцать пять",
    "тридцать пять",
    "десять",
    "ноль пять"
]

HALF = [
    "первого",
    "второго",
    "третьего",
    "четвёртого",
    "пятого",
    "шестого",
    "седьмого",
    "восьмого",
    "девятого",
    "десятого",
    "одинадцатого",
    "двенадцатого"
]


def worded_time():
    return random.choice((f'{random.choice(HOURS)} {random.choice(MINUTES)}', f'пол {random.choice(HALF)}'))

import sys


from get_datetime import MONTHS, NUMBERS
def worded_date():
    month = MONTHS[random.choice(list(MONTHS.keys()))][1]
    day = NUMBERS[random.choice(list(NUMBERS.keys()))][random.choice((1, 2))]
    year = random.randint(1900, 3000)
    return random.choice((f'{day} {month}', f'{month} {day}', f'{day} {month} {year}', f'{month} {day} {year}', f'{month} {year}'))