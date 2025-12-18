import telebot
TOKEN = "8254517535:AAH_8Xu1ZUMhrI7e93tl8SQg3PxYzIG5uj4"
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands = ['a'])
def MICRO(message):
    bot.send_message(message.chat.id, "член")
bot.polling()