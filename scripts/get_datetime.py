import itertools
import re
import datetime
import random

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

MONTHS_KEYS = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}

MONTHS = {
    'jan': ["январь", 'января', "январю", "январе",],
    'feb': ["февраль", 'февраля', "февралю", "феврале",],
    'mar': ["март", 'марта', "марту", "марте",],
    'apr': ["апрель", 'апреля', "апрелю", "апреле",],
    'may': ["май", 'мая', "маю", "мае",],  
    'jun': ["июнь", 'июня', "июню", "июне",],  
    'jul': ["июль", 'июля', "июлю", "июле",],
    'aug': ["август", 'августа', "августу", "августе",],
    'sep': ["сентябрь", 'сентября', "сентябрю", "сентябре"],
    'oct': ["октябрь", 'октября', "октябрю", "октябре",],
    'nov': ["ноябрь", 'ноября', "ноябрю", "ноябре",],
    'dec': ["декабрь", 'декабря', "декабрю", "декабре",]
}

NUMBERS = {
    1: ['один', 'первого', 'первое', 'первому'],
    2: ['два', 'второго', 'второе', 'второму'],
    3: ['три', 'третьего', 'третье', 'третьему'],
    4: ['четыре', 'четвёртого', 'четвёртое', 'четвёртому'],
    5: ['пять', 'пятого', 'пятое', 'пятому'],
    6: ['шесть', 'шестого', 'шестое', 'шестому'],
    7: ['семь', 'седьмого', 'седьмое', 'седьмому'],
    8: ['восемь', 'восьмого', 'восьмое', 'восьмому'],
    9: ['девять', 'девятого', 'девятое', 'девятому'],
    10: ['десять', 'десятого', 'десятое', 'десятому'],
    11: ['одиннадцать', 'одиннадцатого', 'одиннадцатое', 'одиннадцатому'],
    12: ['двенадцать', 'двенадцатого', 'двенадцатое', 'двенадцатому'],
    13: ['тринадцать', 'тринадцатого', 'тринадцатое', 'тринадцатому'],
    14: ['четырнадцать', 'четырнадцатого', 'четырнадцатое', 'четырнадцатому'],
    15: ['пятнадцать', 'пятнадцатого', 'пятнадцатое', 'пятнадцатому'],
    16: ['шестнадцать', 'шестнадцатого', 'шестнадцатое', 'шестнадцатому'],
    17: ['семнадцать', 'семнадцатого', 'семнадцатое', 'семнадцатому'],
    18: ['восемнадцать', 'восемнадцатого', 'восемнадцатое', 'восемнадцатому'],
    19: ['девятнадцать', 'девятнадцатого', 'девятнадцатое', 'девятнадцатому'],
    20: ['двадцать', 'двадцатого', 'двадцатое', 'двадцатому'],
    21: ['двадцать один', 'двадцать первого', 'двадцать первое', 'двадцать первому'],
    22: ['двадцать два', 'двадцать второго', 'двадцать второе', 'двадцать второму'],
    23: ['двадцать три', 'двадцать третьего', 'двадцать третье', 'двадцать третьему'],
    24: ['двадцать четыре', 'двадцать четвёртого', 'двадцать четвёртое', 'двадцать четвёртому'],
    25: ['двадцать пять', 'двадцать пятого', 'двадцать пятое', 'двадцать пятому'],
    26: ['двадцать шесть', 'двадцать шестого', 'двадцать шестое', 'двадцать шестому'],
    27: ['двадцать семь', 'двадцать седьмого', 'двадцать седьмое', 'двадцать седьмому'],
    28: ['двадцать восемь', 'двадцать восьмого', 'двадцать восьмое', 'двадцать восьмому'],
    29: ['двадцать девять', 'двадцать девятого', 'двадцать девятое', 'двадцать девятому'],
    30: ['тридцать', 'тридцатого', 'тридцатое', 'тридцатому'],
    31: ['тридцать один', 'тридцать первого', 'тридцать первое', 'тридцать первому']
}

year_misspellings = ["года", "год", "г", "го", "гда", "га", "гада"]

YEARSIGNIFIER = year_misspellings + [item + '.' for item in year_misspellings] + [item + ',' for item in year_misspellings]

date_words = MONTHS | NUMBERS

date_list = list(itertools.chain.from_iterable(list(date_words.values())))

def most_similar(target, words):
    vectorizer = CountVectorizer(analyzer='char', ngram_range=(1,2))
    vectors = vectorizer.fit_transform([target] + words)
    similarities = cosine_similarity(vectors[0:1], vectors[1:])[0]
    if similarities.max() < 0.6:
        return 'UNRECOGNIZED'
    return words[similarities.argmax()]

def std_value(input_word, all_words):
    for key in all_words:
        if input_word in all_words[key]:
            return key
        
def std_date(input_date):
    input_date = input_date.lower()
    split_date = input_date.split()
    std_date = []

    four_digit_numbers = [int(num) for num in re.findall(r'\b\d{4}\b',input_date)]
    two_digit_numbers = [int(num) for num in re.findall(r'\b\d{1,2}\b',input_date)]
    
    faulty = []
    for token in split_date:
        if token in four_digit_numbers or token in YEARSIGNIFIER or token in two_digit_numbers:
            faulty.append(token)

    for token in faulty:
        split_date.remove(token)

    for word in split_date:
        std_date.append(std_value(most_similar(word, date_list), date_words)) # распознаём актуальные данные

    ints = [word for word in std_date if isinstance(word, int)] 
    if len(ints) > 1:
        first = std_date.index(ints[0])
        second = std_date.index(ints[1])
        if first == second - 1:
            new_int = ints[0] + ints[1]
            std_date[first] = new_int
            std_date.pop(second)

    final_obj = {'date': two_digit_numbers, 'month': [], 'year': four_digit_numbers}
    for obj in std_date:
        if obj in MONTHS.keys():
            final_obj['month'].append(obj)
        elif obj in NUMBERS.keys():
            final_obj['date'].append(obj)
    
    all_values = [len(final_obj['date']), len(final_obj['month']), len(final_obj['year'])]
    if max(all_values) > 1:
        return 'DATE_INVALID: too many objects'
    elif max(all_values) == 0:
        return 'NOT_FOUND: no transcriptable data was found'
    return final_obj

HOURS = {
    60:  ["час", "тринадцать", "13"],
    120:  ["два", "четырнадцать", "14"],
    180:  ["три", "пятнадцать", "15"],
    240:  ["четыре", "шестнадцать", "16"],
    300:  ["пять", "семнадцать", "17"],
    360:  ["шесть", "восемнадцать", "18"],
    420:  ["семь", "девятнадцать", "19"],
    480:  ["восемь", "двадцать", "20"],
    540:  ["девять", "двадцать один", "21"],
    600: ["десять", "двадцать два", "22"],
    660: ["одиннадцать", "двадцать три", "23"],
    720: ["двенадцать", "ноль", "24"]
}

MINUTES = {
    15: ["пятнадцать", "15"],
    30: ["тридцать", "30", "пол первого", "12:30", "половина первого"],
    40: ["сорок", "40"],
    50: ["пятьдесят", "50"],
    45: ["сорок пять", "45"],
    20: ["двадцать", "20"],
    25: ["двадцать пять", "25"],
    35: ["тридцать пять", "35"],
    10: ["десять", "10"],
    5:  ["ноль пять", "5"], 
}

HALF = {
    90:  ["пол второго", "13:30", "половина второго"],
    150:  ["пол третьего", "14:30", "половина третьего"],
    210:  ["пол четвёртого", "15:30", "половина четвёртого"],
    270:  ["пол пятого", "16:30", "половина пятого"],
    330:  ["пол шестого", "17:30", "половина шестого"],
    390:  ["пол седьмого", "18:30", "половина седьмого"],
    450:  ["пол восьмого", "19:30", "половина восьмого"],
    510:  ["пол девятого", "20:30", "половина девятого"],
    570: ["пол десятого", "21:30", "половина десятого"],
    630: ["пол одинадцатого", "22:30", "половина одинадцатого"],
    690: ["пол двенадцатого", "23:30", "половина двенадцатого"]
} 

halfsignifier = ["пол", "пал", "половина", "половине", "полу", "половины", "половина", "палавины", "паловины", "полавины", "палавина", "паловина", "полавина", "палу", "палавине", "паловине", "полавине", "пл", "п"]
minutesignifier = ["пять", "пятб", "пят", "петь", "пть", "ть", "пя", "пить", "петь", "пет"]

DAYNIGHT = {
    0: ["ночь", "утро", "ночи", "утра", "утром", "ночью"],
    1: ["день", "вечер", "вечера", "дня", "вечером", "днём"],
}

time_words = HOURS | MINUTES | HALF

time_list = list(itertools.chain.from_iterable(list(time_words.values())))
daynight = list(itertools.chain.from_iterable(list(DAYNIGHT.values())))

def std_time(input_time):
    input_time = input_time.lower()

    digits = ''.join(re.findall(r'-?\d+', input_time))
    splt = input_time.split()

    hours = []
    minutes = []
    all_obj = []
    digitsAndWords = False
    daynight_correction = False
    half = 0
    next = None
    previous = None

    if len(digits) == 4:
        return datetime.timedelta(hours = int(digits[0] + digits[1]), minutes = int(digits[2] + digits[3]))
    elif len(digits) == 3:
        return datetime.timedelta(hours = int(digits[0]), minutes = int(digits[1] + digits[2]))
    elif len(digits) < 3 and len(digits) > 0:
        digitsAndWords = True
        for token in splt:
            dn = std_value(most_similar(token, daynight), DAYNIGHT)
            if dn in (1, 0):
                daynight_correction = dn
                continue

            try:
                tl = int(token)
                hours.append(tl * 60)
            except:
                tl = std_value(most_similar(token, time_list), time_words)
                minutes.append(tl)

            all_obj.append(tl * 60)
    
    if not digitsAndWords:
        for token in splt:
            if token in minutesignifier and len(hours) != 0:
                all_obj.pop(-1)
                token = previous + ' ' + 'пять'
            previous = token
            
            if token in halfsignifier:
                next = 'пол'
                continue
            
            if next != None:
                token = next + ' ' + token
                next = None
            
            dn = std_value(most_similar(token, daynight), DAYNIGHT)
            if dn in (1, 0):
                daynight_correction = dn
                continue

            tl = std_value(most_similar(token, time_list), time_words)
            all_obj.append(tl)
            if tl in MINUTES:
                minutes.append(tl)
            elif tl in HOURS | HALF:
                hours.append(tl)

    for num in minutes:
        if not (num in all_obj):
            minutes.pop(minutes.index(num))

    for num in hours:
        if not (num in all_obj):
            hours.pop(hours.index(num))

    time = hours + minutes
    if len(time) > 3:
        return 'TIME_INVALID: too many objects'

    if len(hours) == 2:
        complete_time = hours[0] + hours[1] / 60 + 12
    else:
        complete_time = sum(minutes) + sum(hours) + half

    if daynight_correction == 0:
        if complete_time < 720:
            daynight_correction = 0
        else:
            daynight_correction = 720
    elif daynight_correction == 1:
        if complete_time < 300:
            daynight_correction = 0
        else:
            daynight_correction = 720

    return datetime.timedelta(minutes = complete_time + daynight_correction)


def parse_date(message):
    date_obj = std_date(message)
    if isinstance(date_obj, str): # ошибка
        return date_obj
    
    today = datetime.date.today()
    if len(date_obj['year']) > 0:
        year = date_obj['year'][0]
    else:
        year = today.year
    
    if len(date_obj['month']) > 0:
        month = MONTHS_KEYS[date_obj['month'][0]]
    else:
        month = today.month
    
    if len(date_obj['date']) > 0:
        day = date_obj['date'][0]
    else:
        day = today.day

    try:
        return datetime.date(year, month, day)
    except:
        return 'FAILED_TO_PARSE'
    
def parse_time(message):
    try: 
        return std_time(message)
    except:
        return 'FAILED_TO_PARSE'
    

#slicing the message to enhance model performance
rndcontext = [
    "у меня проблема с бронированием билета",
    "как изменить дату вылета?",
    "хочу вернуть билет, что делать?",
    "почему не приходит электронный билет?",
    "помогите выбрать место в салоне",
    "не могу войти в личный кабинет",
    "как добавить багаж к заказу?",
    "рейс задержали, куда обращаться?",
    "хочу оформить страховку для поездки",
    "какой у вас телефон поддержки?"
]
nlp = spacy.load('ru_core_news_sm')
def ngrams(message):
    doc = nlp(message)
    tokens = [token.text for token in doc]
    if len(tokens) < 6:
        doc = nlp(message + ' ' + random.choice(rndcontext))
        tokens = [token.text for token in doc]
    ngram_list = []
    for n in range(2, 7):
        for i in range(len(tokens) - n + 1):
            ngram_list.append(' '.join(tokens[i:i + n]))
    return ngram_list

# searching for single-token date and time
all_single_tokens = {
    "сегодня":     lambda: datetime.date.today(),
    "завтра":      lambda: datetime.date.today() + datetime.timedelta(days=1),
    "вчера":       lambda: datetime.date.today() - datetime.timedelta(days=1),
    "послезавтра": lambda: datetime.date.today() + datetime.timedelta(days=2),
    "позавчера":   lambda: datetime.date.today() - datetime.timedelta(days=2),
    "сейчас":      lambda: datetime.datetime.now().time(),
    "полночь":     lambda: datetime.time(0, 0),
    "полдень":     lambda: datetime.time(12, 0)
}

def is_datetime_singletoken(token):
    return most_similar(token, list(all_single_tokens.keys()))  

def get_datetime_singletoken(sentence):
    tokens = sentence.split()
    datetimes = []
    for token in tokens:
        result = is_datetime_singletoken(token)
        if result != 'UNRECOGNIZED':
            datetime_obj = all_single_tokens[result]()
            if isinstance(datetime_obj, datetime.date):
                datetimes.append(('date', str(datetime_obj), result))
            elif isinstance(datetime_obj, datetime.time):
                datetimes.append(('time', str(datetime_obj), result))
    return datetimes

if __name__ == '__main__':
    print(get_datetime_singletoken('я вылетаю в индию завтра в полночь'))
