import telebot
import spacy
from messages import (
    BOT_TOKEN, MODEL_PATH, ENTITY_TYPES_TO_FIND, ENTITY_LABELS_TRANSLATION,
    get_random_welcome_message, get_random_no_entities_message, get_random_closing_phrase, get_random_s7_tip, ABOUT_BOT_INFO
)

nlp_model = spacy.load(MODEL_PATH)
telegram_bot = telebot.TeleBot(BOT_TOKEN)

def create_main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('О боте')
    btn2 = telebot.types.KeyboardButton('Новый анализ')
    btn3 = telebot.types.KeyboardButton('Совет S7')
    markup.add(btn1, btn2, btn3)
    return markup

@telegram_bot.message_handler(commands=['start'])
def send_welcome_message(message):
    welcome_text = get_random_welcome_message()
    main_menu = create_main_menu()
    telegram_bot.reply_to(message, welcome_text, reply_markup=main_menu)

@telegram_bot.message_handler(func=lambda message: message.text == 'О боте')
def send_about_info(message):
    main_menu = create_main_menu()
    telegram_bot.reply_to(message, ABOUT_BOT_INFO, reply_markup=main_menu)

@telegram_bot.message_handler(func=lambda message: message.text == 'Новый анализ')
def request_new_analysis(message):
    main_menu = create_main_menu()
    telegram_bot.reply_to(message, "Отправьте новое SMS для анализа.", reply_markup=main_menu)

@telegram_bot.message_handler(func=lambda message: message.text == 'Совет S7')
def send_s7_tip(message):
    tip = get_random_s7_tip()
    main_menu = create_main_menu()
    telegram_bot.reply_to(message, tip, reply_markup=main_menu)

@telegram_bot.message_handler(func=lambda message: True)
def process_user_message(message):
    if message.text in ['О боте', 'Новый анализ', 'Совет S7']:
        return

    message_text = message.text
    doc = nlp_model(message_text)

    found_entities = {label: [] for label in ENTITY_TYPES_TO_FIND}

    for entity in doc.ents:
        entity_label_upper = entity.label_.upper()
        if entity_label_upper in found_entities:
            if entity.text not in found_entities[entity_label_upper]:
                found_entities[entity_label_upper].append(entity.text)

    response_parts = [
        f"{ENTITY_LABELS_TRANSLATION.get(label, label)}: {', '.join(values)}"
        for label, values in found_entities.items() if values
    ]

    if response_parts:
        response_text = "\n".join(response_parts)
        closing_text = get_random_closing_phrase()
        response_text += closing_text
    else:
        response_text = get_random_no_entities_message()

    main_menu = create_main_menu()
    telegram_bot.reply_to(message, response_text, reply_markup=main_menu)

def run_bot():
    print("Бот запущен. Ожидание сообщений... (для остановки нажмите Ctrl+C)")
    telegram_bot.polling(none_stop=True, timeout=60, allowed_updates=None)

if __name__ == '__main__':
    run_bot()
