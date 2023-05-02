import telebot
import os
import message_broker as mb

with open('app.yaml') as f:
    import yaml
    settings = yaml.safe_load(f)

bot = telebot.TeleBot(settings['TELEGRAM_TOKEN'])
file_path = os.path.join(os.path.dirname(__file__), 'subscribers.txt')


def send_message(message):
    with open(file_path) as f:
        subscribers = f.read().splitlines()
    for subscriber in subscribers:
        bot.send_message(chat_id=subscriber, text=message)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text.lower()
    if user_message == 'subscribe':
        with open(file_path, 'a') as f:
            f.write(f'{message.chat.id}\n')
        bot.send_message(
            message.chat.id, "You have been subscribed! Be ready to receive some spam!")
    elif "hello" in user_message:
        bot.send_message(message.chat.id, "Hi there!")
    elif "goodbye" in user_message:
        bot.send_message(message.chat.id, "Goodbye!")
    else:
        bot.send_message(
            message.chat.id, "I'm sorry, I didn't understand what you said.")


if __name__ == '__main__':
    bot.polling()
