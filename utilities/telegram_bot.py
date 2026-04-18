import os
from telegram import Update, ReactionTypeEmoji
from telegram.ext import ContextTypes
from mcp import ClientSession
from google import genai
from .mcp_connection_manager import MCPConnectionManager

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ALLOWED_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
    if update.message.chat.id != ALLOWED_ID:
        await update.message.reply_text("YOU ARE NOT ALLOWED TO USE THIS BOT!")
        return
    
    # We successfully received the mcp_session argument!
    
    GENAI_CLIENT = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    grounding_tool = genai.types.Tool(
        google_search=genai.types.GoogleSearch()
    )
    await context.bot.set_message_reaction(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
        reaction=[ReactionTypeEmoji(emoji="⚡")]
    )
    MCP = MCPConnectionManager()
    MCP_SESSION = await MCP.connect()
    res = await GENAI_CLIENT.aio.models.generate_content(
        model="gemma-4-31b-it", contents=update.message.text,
        config=genai.types.GenerateContentConfig(
            temperature=0,
            tools=[MCP_SESSION, grounding_tool],
            tool_config=genai.types.ToolConfig(
                include_server_side_tool_invocations=True,
            ),
        ),
    )
    await update.message.reply_text(res.text)
    await context.bot.set_message_reaction(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
        reaction=[ReactionTypeEmoji(emoji="👍")]
    )
    await MCP.disconnect()
