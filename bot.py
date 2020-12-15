import logging
import os

from telegram.ext import (
    Updater, 
    CommandHandler, 
    MessageHandler, 
    ConversationHandler,
    Filters, 
)

from settings.settings import TELEGRAM_TOKEN
from src.handlers import *

# Enable logging
logging.basicConfig(
    filename = 'logs/info.log',
    format = '%(asctime)s - %(levelname)s - %(message)s',
    encoding = 'utf-8',
    level = logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Conversation handlers
    create_user = ConversationHandler(
        entry_points = [CommandHandler("adduser", add_user)],
        states = {
            CONFIRM: [MessageHandler(Filters.regex('^(Yes|No)'), confirm_user)]
        },
        fallbacks = [CommandHandler("cancel", cancel)]
    )

    dispatcher.add_handler(create_user)

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("listusers", list_users))
    dispatcher.add_handler(CommandHandler("edituser", edit_user))
    dispatcher.add_handler(CommandHandler("deleteuser", delete_user))
    
    # Start the Bot
    updater.start_polling()

    # Run the bot 
    updater.idle()


if __name__ == '__main__':
    main()
