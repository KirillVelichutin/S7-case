import telebot
import spacy
from dotenv import load_dotenv
import os
from messages import (
    MODEL_PATH, ENTITY_TYPES_TO_FIND, ENTITY_LABELS_TRANSLATION,
    get_random_welcome_message, get_random_no_entities_message, 
    get_random_closing_phrase, get_random_s7_tip, ABOUT_BOT_INFO
)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

class TelegramBotService:
    def __init__(self, token, model_path):
        self.bot = telebot.TeleBot(token)
        self.nlp = spacy.load(model_path)
        self._setup_handlers()

    def _setup_handlers(self):
        self.bot.message_handler(commands=['start'])(self.send_welcome_message)
        self.bot.message_handler(func=lambda msg: msg.text == 'О боте')(self.send_about_info)
        self.bot.message_handler(func=lambda msg: msg.text == 'Новый анализ')(self.request_new_analysis)
        self.bot.message_handler(func=lambda msg: msg.text == 'Совет S7')(self.send_s7_tip)
        self.bot.message_handler(func=lambda msg: True)(self.process_user_message)

    def create_main_menu(self):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [
            telebot.types.KeyboardButton('О боте'),
            telebot.types.KeyboardButton('Новый анализ'),
            telebot.types.KeyboardButton('Совет S7')
        ]
        markup.add(*buttons)
        return markup

    def send_welcome_message(self, message):
        welcome_text = get_random_welcome_message()
        main_menu = self.create_main_menu()
        self.bot.reply_to(message, welcome_text, reply_markup=main_menu)

    def send_about_info(self, message):
        main_menu = self.create_main_menu()
        self.bot.reply_to(message, ABOUT_BOT_INFO, reply_markup=main_menu)

    def request_new_analysis(self, message):
        main_menu = self.create_main_menu()
        self.bot.reply_to(message, "Отправьте новое SMS для анализа.", reply_markup=main_menu)

    def send_s7_tip(self, message):
        tip = get_random_s7_tip()
        main_menu = self.create_main_menu()
        self.bot.reply_to(message, tip, reply_markup=main_menu)

    def process_user_message(self, message):
        if message.text in ['О боте', 'Новый анализ', 'Совет S7']:
            return

        doc = self.nlp(message.text)
        found_entities = {label: [] for label in ENTITY_TYPES_TO_FIND}

        for ent in doc.ents:
            label = ent.label_.upper()
            if label in found_entities and ent.text not in found_entities[label]:
                found_entities[label].append(ent.text)

        response_parts = [
            f"{ENTITY_LABELS_TRANSLATION.get(k, k)}: {', '.join(v)}"
            for k, v in found_entities.items() if v
        ]

        if response_parts:
            response_text = "\n".join(response_parts) + get_random_closing_phrase()
        else:
            response_text = get_random_no_entities_message()

        main_menu = self.create_main_menu()
        self.bot.reply_to(message, response_text, reply_markup=main_menu)

    def run(self):
        self.bot.polling(none_stop=True, timeout=60, allowed_updates=None)

service = TelegramBotService(BOT_TOKEN, MODEL_PATH)
service.run()
