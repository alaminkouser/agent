import os
from telegram import Update
from telegram.ext import ContextTypes


def restricted(_):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != int(os.getenv("TELEGRAM_CHAT_ID")):
            await update.message.reply_text("YOU ARE NOT AUTHORIZED TO USE THIS BOT.")
            return
        return await _(update, context)

    return wrapper
