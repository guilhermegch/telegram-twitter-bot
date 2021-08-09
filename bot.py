import logging

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
)

from settings.settings import CHAT_ID, TELEGRAM_TOKEN
from src.handlers import *

# Enable logging
logging.basicConfig(
    filename="logs/info.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def main():
    """Start the bot."""
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Create a filter to only answer CHAT_ID
    chat_filter = Filters.chat(chat_id=int(CHAT_ID))

    # Conversation handlers
    create_user = ConversationHandler(
        entry_points=[CommandHandler("adduser", add_user, filters=chat_filter)],
        states={CONFIRM: [MessageHandler(Filters.regex("^(Yes|No)"), confirm_user)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(create_user)

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command, filters=chat_filter))
    dispatcher.add_handler(CommandHandler("listusers", list_users, filters=chat_filter))
    dispatcher.add_handler(CommandHandler("edituser", edit_user, filters=chat_filter))
    dispatcher.add_handler(
        CommandHandler("deleteuser", delete_user, filters=chat_filter)
    )
    dispatcher.add_handler(
        CommandHandler("startstream", start_stream, filters=chat_filter)
    )
    dispatcher.add_handler(
        CommandHandler("stopstream", stop_stream, filters=chat_filter)
    )

    # Start the Bot
    updater.start_polling()

    # Run the bot
    updater.idle()


if __name__ == "__main__":
    main()
