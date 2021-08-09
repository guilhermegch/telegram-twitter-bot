import logging
import os
import subprocess
import signal

from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove, 
)
from telegram.ext import (
    Updater, 
    CommandHandler, 
    MessageHandler, 
    Filters, 
    CallbackContext, 
    ConversationHandler,
)
from src.twitter import check_user, get_user_data
from src.database import (
    create_database,
    create_user_db, 
    check_user_database, 
    list_users_database, 
    edit_user_database, 
    delete_user_database,
)

# Persistent variables
CONFIRM = 0

# Define handlers
def start(update: Update, context: CallbackContext) -> None:
    """Start the bot"""
    update.message.reply_text("This is a private bot")


def help_command(update: Update, context: CallbackContext) -> None:
    """Configure the /help"""
    update.message.reply_text(
        'This bot send tweets updates from an user to Telegram \n\n'
        'Available commands: \n'
        '/adduser <username> - Adds a new user to the database\n'
        '/listusers - Shows the users added to database\n'
        '/edituser - Edits an username on the database\n'
        '/deleteuser - Remove user from database\n'
        '/startstream - Starts the tweet stream\n'
        '/stopstream - Stops the tweet stream\n'
        '/cancel - Cancel the current operation',
    )


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel the current operation"""

    update.message.reply_text(
        'Canceled!', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def add_user(update: Update, context: CallbackContext):
    """Start the add a new user to database routine"""
    try:
        username = context.args[0].lower()
        
        # Check if user exists
        if not check_user(username):
            update.message.reply_text(f'{username} not founded on Twitter')
            return

        # Get user data
        message = get_user_data(username)
       
        reply_keyboard = [['Yes', 'No']]
        reply = 'Name: ' + message['name'] + '\nBio: '+ message['bio']
        
        update.message.reply_text(reply)
        update.message.reply_photo(message['profile_image'])

        update.message.reply_text(
            'Is this the correct user?',
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
        update.message.reply_text('Usage: /adduser <username>')
        return


def confirm_user(update: Update, context: CallbackContext):
    """Confirm if the username is correct and add it to the database"""
    CONFIRM = update.message.text

    if CONFIRM == 'Yes':
        with open('cache.txt', 'r') as cache:
            username = cache.readline()
        
        # Check if user already exists
        if check_user_database(username):
            update.message.reply_text(
                f'User {username} already exists.',
                reply_markup = ReplyKeyboardRemove()
            )
            os.remove('cache.txt')
            logging.info('Cache file deleted')
            return ConversationHandler.END

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
        update.message.reply_text('Type /adduser <username>')

        os.remove('cache.txt')
        logging.info('Cache file deleted')

        return ConversationHandler.END


def list_users(update: Update, context: CallbackContext):
    """Return the users in database"""
    update.message.reply_text('Checking added users...')
    message = '\n'.join(list_users_database())
    update.message.reply_text(message)


def edit_user(update: Update, context: CallbackContext):
    """Edit user in database"""
    try:
        username = context.args[0].lower()
        new_name = context.args[1].lower()
        
        # Check if user exists
        if not check_user_database(username):
            update.message.reply_text('User not founded on database')
            return

        # Check if user exists on Twitter
        if not check_user(new_name):
            update.message.reply_text(f'{new_name} not founded on Twitter')
            return

        # Get user data
        message = get_user_data(new_name)
        
        reply = 'Name: ' + message['name'] + '\nBio: '+ message['bio']
        
        update.message.reply_text('This is the new user:')
        update.message.reply_text(reply)
        update.message.reply_photo(message['profile_image'])
        
        edit_user_database(username, new_name)
        
        update.message.reply_text(
            f'User edited: {username} now is {new_name}'
        )

    
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /edituser <username> <new name>')
        return


def delete_user(update: Update, context: CallbackContext):
    """Delete user from database"""
    try:
        username = context.args[0].lower()

        # Check if user exists
        if not check_user_database(username):
            update.message.reply_text('User not founded on database')
            return

        update.message.reply_text('Deleting user...')
        delete_user_database(username)
        update.message.reply_text(f'{username} deleted from database')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /deleteuser <username>')
        return


def start_stream(update: Update, context: CallbackContext):
    """Start to stream the tweets"""
    # Check if the process is already running
    process = subprocess.run(['pgrep', 'python', '-a'], capture_output = True)
    out = str(process.stdout).split(' ')
    if 'stream.py' in out:
        update.message.reply_text('Already streaming...')
        return
    chat_id = str(update.message.chat.id)

    update.message.reply_text('Starting the stream...')

    stream = subprocess.Popen(['python', 'stream.py', chat_id])
    
    logging.info(f'{update.message.from_user.username} started the stream')


def stop_stream(update: Update, context: CallbackContext):
    """Stop the tweets streaming"""
    # Check if the process is running
    data = subprocess.run(
        ['pgrep', 'python', '-a'], 
        capture_output = True, 
        text = True
    )
    out = data.stdout.split('\n')

    for processes in out:
        if 'stream.py' in processes:
            pid = processes.split(' ')[0]
            os.kill(int(pid), signal.SIGTERM)

            update.message.reply_text('Stream stopped...')

            logging.info(
                f'{update.message.from_user.username} stopped the stream'
            )
            return
    update.message.reply_text('Stream not running')

