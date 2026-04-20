import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from client.post_init import post_init
from client.command_handler import start

load_dotenv()


telegram_app = (
    ApplicationBuilder()
    .token(os.getenv("TELEGRAM_BOT_TOKEN"))
    .post_init(post_init)
    .build()
)

telegram_app.add_handler(CommandHandler("start", start))


telegram_app.run_polling(drop_pending_updates=True)
