from client.helpers.restricted import restricted
from telegram import Update
from telegram.ext import ContextTypes


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.effective_user.first_name}")
