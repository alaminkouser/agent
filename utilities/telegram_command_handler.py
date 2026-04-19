import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .db import DB


async def handle_command_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ALLOWED_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
    if update.message.chat.id != ALLOWED_ID:
        await update.message.reply_text("YOU ARE NOT ALLOWED TO USE THIS BOT!")
        return

    # Show confirmation
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="clear:yes"),
            InlineKeyboardButton("No", callback_data="clear:no"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Are you sure you want to clear chat history?", reply_markup=reply_markup
    )
