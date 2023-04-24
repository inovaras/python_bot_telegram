import os
from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
import requests
from pprint import pprint
from exceptions import NotFoundCity

load_dotenv()
secret_token = os.getenv('TELEGRAM_TOKEN')
API_KEY = os.getenv('API_KEY')
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

updater = Updater(token=secret_token)
bot = Bot(token=secret_token)


def say_hi(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text=f"""hello"""
                             )


def wake_up(update, context):
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([
        ['/start', '/weather']

    ], resize_keyboard=True)
    context.bot.send_message(chat_id=chat.id,
                             text=
                             f"""Спасибо, что включили меня:) Я могу сообщать погоду""",
                             reply_markup=buttons
                             )


def get_city_coords(update, context):
    try:
        print(update)
        chat = update.effective_chat
        city = update['message']['text']
        GEOCODER_PARAMS['q'] = city
        json = requests.get(GEOCODER_URL, GEOCODER_PARAMS).json()

        if len(json) == 0:
            print('Написан неверно город :(')
            raise NotFoundCity
        lat, lon = json[0]['lat'], json[0]['lon']
        context.bot.send_message(chat_id=chat.id,
                                 text=
                                 """Вычисляются координаты вашего города..."""
                                 )
        context.bot.send_message(chat_id=chat.id,
                                 text=
                                 f"""широта: {lat}, долгота: {lon}"""
                                 )
        weather_str = get_weather(lat, lon)
        chat.send_message(text=weather_str)
    except NotFoundCity as e:
        chat.send_message(text="""'Написан неверно город :('""")


def get_weather(lat, lon):
    WEATHER_PARAMS['lat'] = lat
    WEATHER_PARAMS['lon'] = lon
    json = requests.get(WEATHER_URL, WEATHER_PARAMS).json()
    pprint(json)
    description = json['weather'][0]['description']
    temp = json['main']['temp']
    return f'Погода в городе: {description}, температура: {temp} °C.'


def weather(update, context):
    chat = update.effective_chat
    chat.send_message(text=f"""В каком городе хотите узнать погоду?""")


def main():
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('weather', weather))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, get_city_coords))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
