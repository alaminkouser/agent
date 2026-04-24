import asyncio
import os
from dotenv import load_dotenv
import threading

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from client.post_init import post_init
from client.command_handler import start
from client.message_handler import text
from cron.worker import cron_worker

load_dotenv()


telegram_app = (
    ApplicationBuilder()
    .token(os.getenv("TELEGRAM_BOT_TOKEN"))
    .post_init(post_init)
    .build()
)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))


def start_cron_worker():
    asyncio.run(cron_worker(telegram_app))


threading.Thread(target=start_cron_worker, daemon=True).start()

telegram_app.run_polling(drop_pending_updates=True)
