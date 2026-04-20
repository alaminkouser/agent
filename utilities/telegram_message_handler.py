from pydantic_ai import ModelResponse, TextPart, UserPromptPart, ModelRequest
import os
from telegram import Update, ReactionTypeEmoji
from telegram.ext import ContextTypes
from telegramify_markdown import telegramify
from telegramify_markdown.content import ContentType
from .db import DB
from .system_prompt import system_prompt
from .agent import agent


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ALLOWED_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
    if update.message.chat.id != ALLOWED_ID:
        await update.message.reply_text("YOU ARE NOT ALLOWED TO USE THIS BOT!")
        return

    await context.bot.set_message_reaction(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
        reaction=[ReactionTypeEmoji(emoji="⚡")],
    )

    MESSAGE = update.message.text

    ALL_MESSAGES = DB.execute(
        "SELECT * FROM chat_history ORDER BY id DESC LIMIT 50"
    ).fetchall()

    MODEL_MESSAGES = []

    for row in ALL_MESSAGES:
        print("ROW_1: " + row[1])
        print("ROW_2: " + row[2])
        MODEL_MESSAGES.append(
            ModelRequest(parts=[UserPromptPart(content=row[1])]),
        )
        MODEL_MESSAGES.append(
            ModelResponse(parts=[TextPart(content=row[2])]),
        )

    try:
        AGENT = await agent()
        AI_RESPONSE = await AGENT.run(
            MESSAGE, instructions=system_prompt(), message_history=MODEL_MESSAGES
        )

        REPLY_MD = ""

        if AI_RESPONSE.response.thinking != "":
            REPLY_MD += AI_RESPONSE.response.thinking + "\n\n---\n\n"

        REPLY_MD += AI_RESPONSE.output

        REPLY_MD_FOR_CHUNKS = REPLY_MD

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
        print(e)
        await update.message.reply_text(f"ERROR: {e}")
