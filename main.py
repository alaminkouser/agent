import os
import datetime
import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from utilities.telegram_bot import handle_message

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

async def main():
    TELEGRAM_BOT.add_handler(
        MessageHandler(
            filters.ALL,
            handle_message
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
    TELEGRAM_BOT.run_polling()
