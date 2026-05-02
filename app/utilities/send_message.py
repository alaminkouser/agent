from telegram.constants import ParseMode
from utilities.ensure_string import ensure_string
from telegram import Update

from telegramify_markdown import telegramify
from telegramify_markdown.content import ContentType


async def send_message(update: Update, message: str) -> bool:
    """
    This function formats markdown and sends it to the user.
    The message is formatted using telegramify-markdown.

    If the message is too long, it will be split into multiple messages.

    This will also process mermaid diagrams. And send them as images.
    """
    chunk_list = await telegramify(message, max_message_length=4096)
    for chunk in chunk_list:
        if chunk.content_type == ContentType.TEXT:
            await update.message.reply_text(chunk.text)
        elif chunk.content_type == ContentType.PHOTO:
            await update.message.reply_photo(
                photo=chunk.file_data,
                filename=chunk.file_name,
                caption=chunk.caption_text or None,
                caption_entities=[e.to_dict() for e in chunk.caption_entities] or None,
            )
        elif chunk.content_type == ContentType.FILE:
            if (
                chunk.file_name != None
                and chunk.file_name.endswith(".md")
                and ensure_string(chunk.file_data)
                and len(chunk.file_data) <= 4000
            ):
                text = chunk.file_data.decode("utf-8")
                await update.message.reply_text(
                    f"```md\n{text}```", parse_mode=ParseMode.MARKDOWN_V2
                )
            else:
                await update.message.reply_document(
                    document=chunk.file_data,
                    filename=chunk.file_name,
                    caption=chunk.caption_text or None,
                    caption_entities=[e.to_dict() for e in chunk.caption_entities]
                    or None,
                )
