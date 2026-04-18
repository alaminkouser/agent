import os
import datetime
import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from utilities.telegram_message_handler import handle_message
from utilities.telegram_command_handler import handle_command_clear

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()


async def main():
    TELEGRAM_BOT.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    TELEGRAM_BOT.add_handler(CommandHandler("clear", handle_command_clear))


if __name__ == "__main__":
    asyncio.run(main())
    TELEGRAM_BOT.run_polling()
