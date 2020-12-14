import logging
import os

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, MessageId
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

from settings.settings import TELEGRAM_TOKEN
from src.twitter import check_user, get_user_data
from src.database import create_user_db

# Enable logging
logging.basicConfig(
    filename = 'logs/info.log',
    format = '%(asctime)s - %(levelname)s - %(message)s',
    encoding = 'utf-8',
    level = logging.INFO
)

logger = logging.getLogger(__name__)

# Persistent variables
CONFIRM = 0

# Define handlers
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi! I'm a Twitter bot.")

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'This bot receive live tweets from an user on Telegram \n\n'
        'Availabe commands: \n'
        '/cancel : Cancel the current operation \n'
        '/add_user <username>: Adds a new user to the database'
    )

def tester(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f"Mensagem de {user.first_name}: {update.message.text}")

def add_user(update: Update, context: CallbackContext):
    """Start the add a new user to database routine"""
    try:
        username = context.args[0]
        
        # Check if user exists
        if not check_user(username):
            update.message.reply_text('User not founded')
            return

        # Get user data
        message = get_user_data(username)
       
        reply_keyboard = [['Yes', 'No']]
        reply = 'Name: ' + message['name'] + '\nBio: '+ message['bio']
        
        update.message.reply_text(reply)
        update.message.reply_photo(message['profile_image'])
        update.message.reply_text('Is this the correct user?',
                                    reply_markup=ReplyKeyboardMarkup(
                                        reply_keyboard, 
                                        one_time_keyboard=True
                                    )
                                )
        # Creates a cache file to keep username
        with open('cache.txt', 'w') as cache:
            cache.write(username)
        logging.info(f'Cache created with the username {username}')

        return CONFIRM

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add_user <username>')
        return

def confirm_user(update: Update, context: CallbackContext):
    """Confirm if the username is correct and add it to the database"""
    CONFIRM = update.message.text

    if CONFIRM == 'Yes':
        with open('cache.txt', 'r') as cache:
            username = cache.readline()
        update.message.reply_text(
            f'Adding {username} to database...',
            reply_markup = ReplyKeyboardRemove()
        )
        create_user_db(username)
        update.message.reply_text('Done!')
        
        os.remove('cache.txt')
        logging.info('Cache file deleted')

        return ConversationHandler.END

    else:
        update.message.reply_text(
            'Restarting...',
            reply_markup = ReplyKeyboardRemove()
            )
        update.message.reply_text('Type /add_user <username>')

        os.remove('cache.txt')
        logging.info('Cache file deleted')

        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    '''Cancel the current operation'''
    user = update.message.from_user

    update.message.reply_text(
        'Canceled!', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main():
    """Start the bot."""
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    create_user = ConversationHandler(
        entry_points = [CommandHandler("add_user", add_user)],
        states = {
            CONFIRM: [MessageHandler(Filters.regex('^(Yes|No)'), confirm_user)]
        },
        fallbacks = [CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(create_user)
    
    # on noncommand i.e message - echo the message on Telegram

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()