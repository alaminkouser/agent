import os
from telegram import Update, ReactionTypeEmoji
from telegram.ext import ContextTypes
from mcp import ClientSession
from google import genai
from .mcp_connection_manager import MCPConnectionManager
from telegramify_markdown import telegramify
from telegramify_markdown.content import ContentType
from .db import DB
from .system_prompt import system_prompt
from .status_put import status_put


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ALLOWED_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
    if update.message.chat.id != ALLOWED_ID:
        await update.message.reply_text("YOU ARE NOT ALLOWED TO USE THIS BOT!")
        return

    GENAI_CLIENT = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    grounding_tool = genai.types.Tool(google_search=genai.types.GoogleSearch())
    await context.bot.set_message_reaction(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
        reaction=[ReactionTypeEmoji(emoji="⚡")],
    )

    MESSAGE = update.message.text

    ALL_MESSAGES = DB.execute(
        "SELECT * FROM chat_history ORDER BY id DESC LIMIT 50"
    ).fetchall()

    CONTENT_LIST = [
        genai.types.Content(
            role="system", parts=[genai.types.Part(text=system_prompt())]
        )
    ]
    for row in ALL_MESSAGES:
        CONTENT_LIST.append(
            genai.types.Content(role="user", parts=[genai.types.Part(text=row[1])])
        )
        CONTENT_LIST.append(
            genai.types.Content(role="model", parts=[genai.types.Part(text=row[2])])
        )

    CONTENT_LIST.append(
        genai.types.Content(role="user", parts=[genai.types.Part(text=MESSAGE)])
    )

    MCP: MCPConnectionManager | None = None
    try:
        MCP = MCPConnectionManager()
        MCP_SESSION = await MCP.connect()

        AI_RESPONSE = await GENAI_CLIENT.aio.models.generate_content(
            model="gemma-4-31b-it",
            contents=CONTENT_LIST,
            config=genai.types.GenerateContentConfig(
                temperature=0,
                tools=[MCP_SESSION, status_put, grounding_tool],
                tool_config=genai.types.ToolConfig(
                    include_server_side_tool_invocations=True,
                ),
            ),
        )

        TOOLS_USED = []
        for content in AI_RESPONSE.automatic_function_calling_history:
            for part in content.parts:
                if part.function_call:
                    TOOLS_USED.append(part.function_call.name)

        REPLY_MD = AI_RESPONSE.text

        REPLY_MD_FOR_CHUNKS = REPLY_MD
        if TOOLS_USED:
            REPLY_MD_FOR_CHUNKS = f"{REPLY_MD}\n\n**TOOLS USED**\n\n- {"\n- ".join(TOOLS_USED)}"

        CHUNKS = await telegramify(REPLY_MD_FOR_CHUNKS, max_message_length=4090)
        for chunk in CHUNKS:
            if chunk.content_type == ContentType.TEXT:
                await update.message.reply_text(
                    chunk.text,
                    entities=[e.to_dict() for e in chunk.entities],
                )
            elif chunk.content_type == ContentType.PHOTO:
                await update.message.reply_photo(
                    photo=chunk.file_data,
                    filename=chunk.file_name,
                    caption=chunk.caption_text or None,
                    caption_entities=[e.to_dict() for e in chunk.caption_entities]
                    or None,
                )
            elif chunk.content_type == ContentType.FILE:
                await update.message.reply_document(
                    document=chunk.file_data,
                    filename=chunk.file_name,
                    caption=chunk.caption_text or None,
                    caption_entities=[e.to_dict() for e in chunk.caption_entities]
                    or None,
                )

        await context.bot.set_message_reaction(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
            reaction=[ReactionTypeEmoji(emoji="👍")],
        )

        DB.execute(
            "INSERT INTO chat_history (message, response) VALUES (?, ?)",
            (MESSAGE, REPLY_MD),
        )
        DB.commit()
    except Exception as e:
        await update.message.reply_text(f"ERROR: {e}")
    finally:
        if MCP is not None:
            await MCP.disconnect()
