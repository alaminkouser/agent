import os
import asyncio
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    CallbackQueryHandler,
)
from telegram import Update
from utilities.telegram_message_handler import handle_message
from utilities.telegram_command_handler import handle_command_clear
from utilities.telegram_command_clear_callback import handle_command_clear_callback
from utilities.telegram_post import telegram_post_init, telegram_post_shutdown

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()


async def main():
    TELEGRAM_BOT.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    TELEGRAM_BOT.add_handler(CommandHandler("clear", handle_command_clear))
    TELEGRAM_BOT.add_handler(CallbackQueryHandler(handle_command_clear_callback))

    TELEGRAM_BOT.post_init = telegram_post_init
    TELEGRAM_BOT.post_shutdown = telegram_post_shutdown


if __name__ == "__main__":
    asyncio.run(main())
    TELEGRAM_BOT.run_polling(allowed_updates=Update.ALL_TYPES)
