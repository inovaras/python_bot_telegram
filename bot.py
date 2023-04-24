from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from pprint import pprint
import requests
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
secret_token = os.getenv('TELEGRAM_TOKEN')
API_KEY = os.getenv('API_KEY')

URL_CAT = 'https://api.thecatapi.com/v1/images/search'
URL_DOG = 'https://api.thedogapi.com/v1/images/search'
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
GEOCODER_URL = 'http://api.openweathermap.org/geo/1.0/direct'
WEATHER_PARAMS = {
    'appid': API_KEY,
    'units': 'metric',
    'lang': 'ru'
}

GEOCODER_PARAMS = {
    'appid': API_KEY
}
buttons = ReplyKeyboardMarkup([
    ['/newcat', '/newdog'],
    ['/time', '/weather'],

], resize_keyboard=True)

updater = Updater(token=secret_token)
bot = Bot(token=secret_token)


def print_weather(update, context, weather):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text=weather)


def get_city_coords(update, context):
    GEOCODER_PARAMS['q'] = update['message']['text']
    json = requests.get(GEOCODER_URL, GEOCODER_PARAMS).json()

    if len(json) == 0:
        print('Что-то пошло не так :(')
        exit()
    lat, lon = json[0]['lat'], json[0]['lon']

    weather = get_weather(lat, lon)
    print_weather(update, context, weather)


def get_weather(lat, lon):
    WEATHER_PARAMS['lat'] = lat
    WEATHER_PARAMS['lon'] = lon
    json = requests.get(WEATHER_URL, WEATHER_PARAMS).json()
    pprint(json)
    description = json['weather'][0]['description']
    temp = json['main']['temp']
    return f'Погода. {description.capitalize()}, температура: {temp} °C.'


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
                             text='Привет')


def give_msg(update, context):
    chat = update.effective_chat
    msg = update['message']['text']
    context.bot.send_message(chat_id=chat.id,
                             text=msg)


def say_bye(update, context):

    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text=f'Пока, {chat.first_name}')


def wake_up(update, context):
    chat = update.effective_chat
    name = chat.first_name

    context.bot.send_message(chat_id=chat.id,
                             text=
                             f"""Спасибо, что включили меня, {name}, чем могу быть полезен?:) Еды пока нет, могу предложить котиков, для этого нажмите на кнопку /newcat, чтобы узнать который час нажмите на кнопку  /time""",
                             reply_markup=buttons
                             )
    bot.send_photo(chat.id, get_new_image(URL_CAT, URL_DOG))


def give_new_cat(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image(URL_CAT, URL_DOG))


def give_new_dog(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image(URL_DOG, URL_CAT))


def send_weather(update, context):
    chat = update.effective_chat
    text = 'Отправь мне город и я скажу какая погода там :)'
    bot.send_message(chat.id, text, reply_markup=buttons)
    updater.start_polling()
    updater.dispatcher.add_handler(MessageHandler(Filters.text, get_city_coords))


def give_answer(update, context):
    print(update)
    print(update['message']['text'])


def main():
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newcat', give_new_cat))
    updater.dispatcher.add_handler(CommandHandler('newdog', give_new_dog))
    updater.dispatcher.add_handler(CommandHandler('time', give_time))
    updater.dispatcher.add_handler(CommandHandler('date', give_date))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('привет'), say_hi))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('пока'), say_bye))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, give_answer))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
