from telegram import Update
from telegram.ext import ContextTypes

from client.helpers.restricted import restricted


@restricted
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query_data = query.data

    if query_data.startswith("notebook:d:"):
        await query.edit_message_text(
            text=f"Notebook selected: {query_data.split(":")[2]}"
        )

    if query_data.startswith("notebook:f:"):
        await query.edit_message_text(
            text=f"Notebook selected: {query_data.split(":")[2]}"
        )
