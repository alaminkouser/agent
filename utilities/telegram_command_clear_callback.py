from .db import DB
from telegram import Update
from telegram.ext import ContextTypes


async def handle_command_clear_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.data == "clear:yes":
        DB.execute("DELETE FROM chat_history")
        DB.commit()
        await query.edit_message_text("CHAT HISTORY CLEARED!")

    elif query.data == "clear:no":
        await query.edit_message_text("OPERATION CANCELLED!")
