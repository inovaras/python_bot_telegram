from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
import requests
import datetime
import os
from dotenv import load_dotenv


load_dotenv()
secret_token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('CHAT_ID')

URL_CAT = 'https://api.thecatapi.com/v1/images/search'
URL_DOG = 'https://api.thedogapi.com/v1/images/search'


updater = Updater(token=secret_token)
bot = Bot(token=secret_token)


def give_time(update, context):
    now = datetime.datetime.now()
    chat = update.effective_chat

    context.bot.send_message(chat_id=chat.id,
                             text=now.strftime('%H:%M:%S'))


def give_date(update, context):
    now = datetime.datetime.now()
    chat = update.effective_chat

    context.bot.send_message(chat_id=chat.id,
                             text=now.strftime('%d.%m.%Y'))


def get_new_image(URL_1, URL_2):
    try:
        response = requests.get(URL_1).json()
    except Exception as e:
        print(e)
        new_url = URL_2
        response = requests.get(new_url).json()

    return response[0]['url']


def say_hi(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text=f'Привет, {chat.first_name}, я PrettyKittyBot')


def wake_up(update, context):
    chat = update.effective_chat
    name = chat.first_name
    buttons = ReplyKeyboardMarkup([
        ['/newcat', '/newdog'],
        ['/time', '/date'],

    ], resize_keyboard=True)
    context.bot.send_message(chat_id=chat.id,
                             text=
                             f"""Спасибо, что включили меня, {name}, чем могу быть полезен?:)""",
                             reply_markup=buttons
    )


def give_new_cat(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image(URL_CAT, URL_DOG))


def give_new_dog(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image(URL_DOG, URL_CAT))


def main():
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newcat', give_new_cat))
    updater.dispatcher.add_handler(CommandHandler('newdog', give_new_dog))
    updater.dispatcher.add_handler(CommandHandler('time', give_time))
    updater.dispatcher.add_handler(CommandHandler('date', give_date))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

