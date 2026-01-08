import pandas as pd
import re
import spacy
import json


def find_passports(text):
    df = pd.read_csv('./data/passports_regions_data.csv', encoding='utf-8')
    val_passport_codes = list(map(str, df['Код в серии паспорта РФ'].tolist()))

    df = pd.read_csv('./data/international_data.csv', encoding='utf-8')
    val_international_codes = list(map(str, df['Код принадлежности документа'].tolist()))


    passports = []

    passport_pattern = r'\b\d{10}\b'
    international_pattern = r'\b\d{9}\b'

    passport_match = re.search(passport_pattern, text)

    international_match = re.search(international_pattern, text)

    if passport_match:
        passport = re.findall(passport_pattern, text)
        for inst in passport:
            if inst[:2] in val_passport_codes:
                inst = inst[:4] + ' ' + inst[4:]
                ent_type = "passport"

            passports.append({
                "token": inst,
                "tag": ent_type
            })

    if international_match:
        international = re.findall(international_pattern, text)
        for inst in international:
            if inst[:2] in val_international_codes:
                inst = inst[:2] + ' ' + inst[2:]
                ent_type = "international"

            passports.append({
                "token": inst,
                "tag": ent_type
            })

    return passports

def find_phones(text):
    phone_pattern = r'(?:\s*\+\s*?7\d{9}|8\d{10})'

    phones = []

    phone_match = re.search(phone_pattern, text)

    if phone_match:
        phone = re.findall(phone_pattern, text)
        phone = [inst.replace(' ', '') for inst in phone]
        for inst in phone:
            if inst[:2] == "+7" or inst[:1] ==  "8":
                inst = '+7 (' + inst[2:5] + ') ' + inst[5:8] + '-' + inst[8:10] + '-' + inst[10:]

            ent_type = "phone"

            phones.append({
                "token": inst,
                "tag": ent_type
            })

    return phones

def find_emails(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,}\b'

    emails = []

    email_match = re.search(email_pattern, text)

    if email_match:
        email = re.findall(email_pattern, text)
        for inst in email:
            ent_type = "email"

            emails.append({
                "token": inst,
                "tag": ent_type
            })

    return emails

def find_iata(text):
    df = pd.read_csv('./data/airports_rus.csv', encoding='utf-8')
    val_iata_codes = list(map(str, df['Код ИАТА'].tolist()))

    iatas = []

    iata_pattern = r'\b[A-Z]{3}\b'

    iata_match = re.search(iata_pattern, text)

    if iata_match:
        iata = re.findall(iata_pattern, text)
        for inst in iata:
            inst = inst.upper()
            if inst in val_iata_codes:
                ent_type = "iata"

                iatas.append({
                    "token": inst,
                    "tag": ent_type
                })

    return iatas

def find_order_num(text):
    order_num_pattern = r'\b[A-Z0-9]{6}\b'

    order_nums = []

    order_num_match = re.search(order_num_pattern, text)

    if order_num_match:
        order_num = re.findall(order_num_pattern, text)
        for inst in order_num:
            inst = inst.upper()
            ent_type = "order_number"

            order_nums.append({
                "token": inst,
                "tag": ent_type
            })

    return order_nums

def find_ticket_num(text):
    ticket_num_pattern = r'\b585\d{10}\b'

    ticket_nums = []

    ticket_num_match = re.search(ticket_num_pattern, text)

    if ticket_num_match:
        ticket_num = re.findall(ticket_num_pattern, text)
        for inst in ticket_num:
            inst = inst.upper()
            ent_type = "ticket_number"

            ticket_nums.append({
                "token": inst,
                "tag": ent_type
            })

    return ticket_nums

def find_flight(text):
    flight_pattern = r'\bS7\s?\d{1,4}\b'

    flights = []

    flight_match = re.search(flight_pattern, text)

    if flight_match:
        flight = re.findall(flight_pattern, text)
        for inst in flight:
            inst = inst.upper()
            true_inst = inst[:2] + ' ' + inst[2:]
            text = text.replace(inst, true_inst)
            ent_type = "flight"

            flights.append({
                "token": true_inst,
                "tag": ent_type
            })

    return flights, text


def process_request(user_message):
    # Handle potential encoding issues in the input
    try:
        text = user_message.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError:
        # Clean the text if there are encoding issues
        text = user_message.encode('utf-8', errors='replace').decode('utf-8')

    text = re.sub(r'(\d)[\s*\-\(\)]+(?=\d)', r'\1', text)

    ents_data = []

    flights, text = find_flight(text)
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
            if order_num not in ents_data:
                ents_data.append(order_num)


    return [(ent['tag'], ent['token']) for ent in ents_data]

if __name__ == '__main__':
    user_message = user_message = "я вылетаю в париж 31 декабря S79520, меня зовут сёмин никита мой номер телефона 8 911-280-08-12, мой номер паспорта 40- 18 -295647 я вылетаю из домодедово в париж 64-7202067 ABA 34C0Z0, 5854033941712 test123@mail.museum"
    print(process_request(user_message))