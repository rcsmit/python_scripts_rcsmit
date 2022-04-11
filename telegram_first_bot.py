from telegram.ext import Updater
import logging
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
import random


updater = Updater(token='5203654281:AAHeKkFM6x20qmJFdWrWQbIUlLmjH0yhnLQ', use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def quote(update: Update, context: CallbackContext):
    quotes_list = ["Be alive", "Be happy", "Be healthy"]
    quote_selected = random.choice(quotes_list)
    context.bot.send_message(chat_id=update.effective_chat.id, text=quote_selected)


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def stop(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot has stopped")
    updater.stop()

def caps(update: Update, context: CallbackContext):
    if len(context.args)==0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Message text is empty")
    else:
        text_caps = ' '.join(context.args).upper()
        context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def inline_caps(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Message text is empty")
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)

def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

caps_handler = CommandHandler('caps', caps)
dispatcher.add_handler(caps_handler)


quote_handler = CommandHandler('quote', quote)
dispatcher.add_handler(quote_handler)

inline_caps_handler = InlineQueryHandler(inline_caps)
dispatcher.add_handler(inline_caps_handler)

stop_handler = CommandHandler('stop', stop)
dispatcher.add_handler(stop_handler)

#  This handler must be added last. If you added it sooner, it would be triggered before the CommandHandlers had a chance to look at the update.
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
# This should be used most of the time, since start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()
