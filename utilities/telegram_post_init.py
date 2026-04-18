from telegram import BotCommand

async def telegram_post_init(application):
    await application.bot.set_my_commands(commands = [
        BotCommand(command="clear", description="Clear chat history")
    ])