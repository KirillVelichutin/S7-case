import telebot
from scripts.trainer import load_model

nlp = load_model()

BOT_TOKEN = "8593188547:AAGGWTBcq6UOi_QTtiaclAXEfzwqoPJ0awY"
bot = telebot.TeleBot(BOT_TOKEN)

ENTITIES_TO_FIND = [
    'PHONE', 'PASSPORT', 'NAME', 'DOB', 'EMAIL', 'AIRPORT', 'FLIGHT', 'CITY',
    'TIME', 'DATE', 'INTERNATIONAL', 'TICKET_NUMBER', 'ORDER_NUMBER', 'COUNTRY',
    'BOOKING_REF', 'BOARDING_PASS', 'EMD_NUMBER', 'TICKET', 'BIRTH_CERTIFICATE', 'VISA'
]

LABELS_RU = {
    'PHONE': 'Телефон',
    'PASSPORT': 'Паспорт',
    'NAME': 'Имя',
    'DOB': 'Дата рождения',
    'EMAIL': 'Email',
    'AIRPORT': 'Аэропорт',
    'FLIGHT': 'Рейс',
    'CITY': 'Город',
    'TIME': 'Время',
    'DATE': 'Дата',
    'INTERNATIONAL': 'Заграничный паспорт',
    'TICKET_NUMBER': 'Номер билета',
    'ORDER_NUMBER': 'Номер заказа',
    'COUNTRY': 'Страна',
    'BOOKING_REF': 'Номер бронирования',
    'BOARDING_PASS': 'Посадочный талон',
    'EMD_NUMBER': 'Номер EMD',
    'TICKET': 'Билет',
    'BIRTH_CERTIFICATE': 'Свидетельство о рождении',
    'VISA': 'Виза',
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне SMS-сообщение, и я извлеку из него сущности.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text
    doc = nlp(user_message)

    entities = {label: [] for label in ENTITIES_TO_FIND}

    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)

    response_parts = [
        f"{LABELS_RU.get(label, label)}: {', '.join(values)}"
        for label, values in entities.items() if values
    ]

    response = "\n".join(response_parts) if response_parts else "Сущности не найдены."
    bot.reply_to(message, response)

if __name__ == '__main__':
    bot.polling()