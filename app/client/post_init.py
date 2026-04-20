import os


async def post_init(telegram_app):
    await telegram_app.bot.send_message(
        chat_id=int(os.getenv("TELEGRAM_CHAT_ID")), text="BOT IS ONLINE"
    )
