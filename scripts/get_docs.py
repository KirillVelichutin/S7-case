import pandas as pd
import re


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
        start, end = match.span()

        if len(raw) == 10 and raw[:2] in val_passport_codes:
            formatted = raw[:4] + ' ' + raw[4:]
            passports.append({
                "token": formatted,
                "tag": "PASSPORT",
                "span": (start, end)
            })

    for match in re.finditer(international_pattern, text):
        raw = match.group()
        start, end = match.span()

        if len(raw) == 9 and raw[:2] in val_international_codes:
            formatted = raw[:2] + ' ' + raw[2:]
            passports.append({
                "token": formatted,
                "tag": "INTERNATIONAL",
                "span": (start, end)
            })

    return passports

def find_emails(text):    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    
    emails = []
    
    for match in re.finditer(email_pattern, text):
        inst = match.group()
        start, end = match.span()
        
        ent_type = "EMAIL"
        
        emails.append({
            "token": inst,
            "tag": ent_type,
            "span": (start, end)
        })
            
    return emails

def find_phones(text):    
    phone_pattern = r'(?:\+?7|\b8)[\s\-()]?\d{3}[\s\-()]?\d{3}[\s\-()]?\d{2}[\s\-()]?\d{2}'
    
    phones = []
    
    for match in re.finditer(phone_pattern, text):
        raw_match = match.group()
        start, end = match.span()
        
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
            "span": (start, end)
        })
    
    return phones

def find_iata(text):
    df = pd.read_csv('../data/airports_rus.csv')
    val_iata_codes = list(map(str, df['Код ИАТА'].tolist()))
    
    iatas = []
    
    iata_pattern = r'\b[A-Za-z]{3}\b'
    
    for match in re.finditer(iata_pattern, text):
        raw_code = match.group().upper()
        start, end = match.span()
        
        if raw_code in val_iata_codes:
            iatas.append({
                "token": raw_code,
                "tag": "IATA",
                "span": (start, end)
            })
    
    return iatas

def find_order_num(text):
    order_num_pattern = r'\b(?!S7)(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9]{6,7}\b'
    
    order_nums = []
    
    for match in re.finditer(order_num_pattern, text):
        raw_token = match.group()
        start, end = match.span()
        
        normalized_token = raw_token.upper()
        ent_type = "ORDER_NUMBER"
        
        order_nums.append({
            "token": normalized_token,
            "tag": ent_type,
            "span": (start, end)
        })
    
    return order_nums

def find_ticket_num(text):
    ticket_num_pattern = r'\b585\d{10}\b'
    
    ticket_nums = []
    
    for match in re.finditer(ticket_num_pattern, text):
        raw_token = match.group()
        start, end = match.span()
        
        normalized_token = raw_token.upper()
        ent_type = "TICKET_NUMBER"
        
        ticket_nums.append({
            "token": normalized_token,
            "tag": ent_type,
            "span": (start, end)
        })
    
    return ticket_nums

def find_flight(text):
    flight_pattern = r'\bS7\s?\d{1,4}\b'
    
    flights = []
    
    for match in re.finditer(flight_pattern, text):
        raw_match = match.group()
        start, end = match.span()
        
        normalized = "S7 " + raw_match[2:].replace(" ", "")
        ent_type = "FLIGHT"
        
        flights.append({
            "token": normalized,
            "tag": ent_type,
            "span": (start, end)
        })
    
    return flights


def process_request(user_message):
    # Handle potential encoding issues in the input
    try:
        text = user_message.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError:
        # Clean the text if there are encoding issues
        text = user_message.encode('utf-8', errors='replace').decode('utf-8')

    text = re.sub(r'(\d)[\s*\-\(\)]+(?=\d)', r'\1', text)

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
            if order_num not in ents_data:
                ents_data.append(order_num)


    return [(ent['tag'], ent['token']) for ent in ents_data]

if __name__ == '__main__':
    user_message = user_message = "я вылетаю в париж 31 декабря S79520, меня зовут сёмин никита мой номер телефона 8 911-280-08-12, мой номер паспорта 40- 18 -295647 я вылетаю из домодедово в париж 64-7202067 ABA 34C0Z0, 5854033941712 test123@mail.museum"
    print(process_request(user_message))