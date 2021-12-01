import telebot
from decouple import config

TOKEN_BOT = config('TOKEN_BOT')
bot = telebot.TeleBot(TOKEN_BOT)


@bot.message_handler(commands=['help'])
def help_info(message):
    bot.send_message(message.from_user.id,
                     'Список комманд:\n/lowprice - вывод самых дешёвых отелей в городе'
                     '\n/highprice - вывод самых дорогих отелей в городе'
                     '\n/bestdeal - вывод отелей, наиболее подходящих по цене и расположению от центра'
                     '\n/history - вывод истории поиска отелей'
                     )


@bot.message_handler(commands=['hello-world'])
def say_hello(message):
    bot.send_message(message.from_user.id, "Привет!")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.from_user.id, "Привет!")
    else:
        bot.send_message(message.from_user.id, "Неизвестная команда!")

bot.polling(none_stop=True, interval=0)
# venv\Scripts\activate.bat
# pip freeze > requirements.txt
