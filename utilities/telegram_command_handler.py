import os
from telegram import Update
from telegram.ext import ContextTypes
from .db import DB

async def handle_command_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ALLOWED_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
    if update.message.chat.id != ALLOWED_ID:
        await update.message.reply_text("YOU ARE NOT ALLOWED TO USE THIS BOT!")
        return
    
    DB.execute("DELETE FROM chat_history")
    DB.commit()
    
    await update.message.reply_text("CHAT HISTORY CLEARED!")
        