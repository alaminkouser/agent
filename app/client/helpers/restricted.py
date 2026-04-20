import os
from telegram import Update
from telegram.ext import ContextTypes


def restricted(_):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != int(os.getenv("TELEGRAM_CHAT_ID")):
            await update.message.reply_text("You are not authorized to use this bot.")
            return
        return await _(update, context)

    return wrapper
