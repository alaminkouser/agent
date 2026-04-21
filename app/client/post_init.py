import os
from agents.main import agent_main

agent_main = agent_main()


async def post_init(telegram_app):
    await telegram_app.bot.send_message(
        chat_id=int(os.getenv("TELEGRAM_CHAT_ID")), text="BOT IS ONLINE"
    )

    telegram_app.bot_data["agent_main"] = agent_main
