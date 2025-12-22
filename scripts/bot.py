from dotenv import load_dotenv
import os

import telebot
from telebot import types

load_dotenv()
KEY = os.getenv("KEY")

from main import S7ner

ner = S7ner()
telegram_bot = telebot.TeleBot(KEY)


@telegram_bot.message_handler(commands=['start'])
def start(message):
    telegram_bot.send_message(message.chat.id, "Добро поаловать в демонстрационный бот S7NER!\nПришлите боту сообщение содержащее, имя, номер паспорта, телефон, дату, вермя, и бот распознает их и преведёт к стандартному виду!")

@telegram_bot.message_handler()
def process_user_message(message):
    message_text = message.text
    tags = ner.get_entities(message_text.lower())  
    
    if len(tags) == 0:
        reply = "❌ не нашли ценной информации ..."
    else:
        reply = "🧠 *Распознанные сущности:*\n"
        reply += "━━━━━━━━━━━━━━━━━━━━\n"
        for tag in tags:
            reply += f"**{tag[0]}**  →  `{tag[1]}`\n"
        reply += "━━━━━━━━━━━━━━━━━━━━"
    telegram_bot.reply_to(message, reply, parse_mode='Markdown')

def run_bot():
    print("Up and running!")
    telegram_bot.polling(none_stop=True, timeout=60, allowed_updates=None)

if __name__ == '__main__':
    run_bot()