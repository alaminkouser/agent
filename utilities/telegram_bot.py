import os
from telegram import Update
from telegram.ext import ContextTypes
from mcp import ClientSession


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ALLOWED_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
    if update.message.chat.id != ALLOWED_ID:
        await update.message.reply_text("YOU ARE NOT ALLOWED TO USE THIS BOT!")
        return
    
    # We successfully received the mcp_session argument!
    MCP_SESSION: ClientSession = context.bot_data.get("mcp_session")

    print(MCP_SESSION)
    await update.message.reply_text(update.message.text)