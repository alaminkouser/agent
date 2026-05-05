import os
from telegram import BotCommand
from agents.main import agent_main

agent_main = agent_main()


async def post_init(telegram_app):
    """
    This function is called after the bot is initialized.
    It sends a message to the user and stores the agent in the bot data.

    The user is defined in the .env file as TELEGRAM_CHAT_ID.
    """
    await telegram_app.bot.set_my_commands(
        [
            BotCommand("start", "Start a new Conversation"),
            BotCommand("notebook", "Navigate Notebook"),
            BotCommand("notebook_commit", "Make a Commit in Notebook"),
        ]
    )
    await telegram_app.bot.send_message(
        chat_id=int(os.getenv("TELEGRAM_CHAT_ID")), text="BOT IS ONLINE"
    )

    telegram_app.bot_data["agent_main"] = agent_main
