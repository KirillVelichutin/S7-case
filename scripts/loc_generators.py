import random
import re

from faker.providers import BaseProvider
from faker_airtravel import AirTravelProvider

class RussianDocumentsProvider(BaseProvider):
    def international_passport(self):
        series = random.choice(['53', '60', '61', '62', '63', '64', '65', '70', '71', '72'])
        number = f"{self.random_int(1000000, 9999999)}"
        
        formats = [
            f"{series} {number}",
            f"{series}{number}",
            f"{series}-{number}",
            f"серия {series} номер {number}",
            f"загранпаспорт {series} {number}"
        ]
        return random.choice(formats)
    
    def birth_certificate(self):
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
            visa_number = f"{self.random_int(10000000, 99999999)}"
            formats = [visa_number, f"виза № {visa_number}"]
        
        return random.choice(formats)

class AviationDocumentsProvider(BaseProvider):
    def ticket_number(self):
        airline_codes = ['421', '555', '262', '124']
        airline = random.choice(airline_codes)
        number = f"{self.random_int(1000000000, 9999999999)}"

        return f"{airline}{number}"
    
    def booking_ref(self):
        chars = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'
        pnr = ''.join(random.choices(chars, k=6))
        
        formats = [
            pnr,
            f"{pnr[:3]}-{pnr[3:]}",
            f"бронь {pnr}",
            f"PNR {pnr}",
            f"код {pnr}",
            f"номер брони {pnr}",
            f"бронирование {pnr}"
        ]
        return random.choice(formats)
    
    def boarding_pass(self):
        if random.random() > 0.5:
            return self.booking_ref()
        else:
            number = f"{self.random_int(1000000000, 9999999999999)}"
            formats = [
                number,
                f"посадочный {number}",
                f"талон {number}",
                f"BP{number}",
                f"посадочный талон {number}"
            ]
            return random.choice(formats)
    
    def emd_number(self):
        airline_codes = ['421']
        airline = random.choice(airline_codes)
        number = f"{self.random_int(1000000000, 9999999999)}"
        
        formats = [
            f"{airline} {number}",
            f"EMD {airline} {number}",
            f"{airline}{number}",
            f"документ EMD {airline} {number}",
            f"номер EMD {airline} {number}"
        ]
        return random.choice(formats)
    
    def order_number(self):
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    
        random_chars = ''.join(random.choices(characters, k=7))
        
        formats = [
            random_chars,
            f"ORD{random_chars}",
            #f"ORDER-{random_chars}",
            #f"ЗАКАЗ{random_chars}",
            #f"№{random_chars}",
            #f"заказ №{random_chars}",
            f"{random_chars[:3]}-{random_chars[3:]}",
            f"{random_chars[:2]}{random_chars[2:4]}{random_chars[4:]}",
        ]
        return random.choice(formats)

class RussianAviationProvider(BaseProvider):
    def __init__(self, generator):
        super().__init__(generator)
        self.documents_provider = RussianDocumentsProvider(generator)
        self.aviation_provider = AviationDocumentsProvider(generator)
    
    def russian_airline(self):
        airlines = ['S7 Airlines', 'Аэрофлот', 'Уральские авиалинии', 'Победа', 'Ютейр', 'Россия']
        return random.choice(airlines)
    
    
    def russian_flight_number(self):
        airlines = ['S7', 'SU', 'U6', 'DP', '5N', 'WZ', 'FV']
        airline = random.choice(airlines)
        number = self.random_int(1, 9999)
        return f"{airline}{number}"
    
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

def setup_faker_providers(faker_instance):
    faker_instance.add_provider(AirTravelProvider)
    faker_instance.add_provider(RussianAviationProvider)
    return faker_instance

def get_all_document_types():
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