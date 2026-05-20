from telegram.constants import ParseMode
from utilities.ensure_string import ensure_string
from telegram import Update

from telegramify_markdown import telegramify, Text, Photo
from telegramify_markdown.config import get_runtime_config
from telegramify_markdown.content import ContentType


async def send_message(update: Update, message: str) -> bool:
    """
    This function formats markdown and sends it to the user.
    The message is formatted using telegramify-markdown.

    If the message is too long, it will be split into multiple messages.

    This will also process mermaid diagrams. And send them as images.
    """
    if not update.message:
        return False
    cfg = get_runtime_config()
    cfg.markdown_symbol.heading_level_1 = "# "
    cfg.markdown_symbol.heading_level_2 = "## "
    cfg.markdown_symbol.heading_level_3 = "### "
    cfg.markdown_symbol.heading_level_4 = "#### "
    cfg.markdown_symbol.heading_level_5 = "##### "
    cfg.markdown_symbol.heading_level_6 = "###### "
    chunk_list = await telegramify(message, max_message_length=4096)
    for chunk in chunk_list:
        if isinstance(chunk, Text):
            print("TEST:SM:TEXT")
            await update.message.reply_text(
                chunk.text,
                entities=[e.to_dict() for e in chunk.entities]
            )
        elif isinstance(chunk, Photo):
            print("TEST:SM:PHOTO")
            await update.message.reply_photo(
                photo=chunk.file_data,
                filename=chunk.file_name,
                caption=chunk.caption_text or None,
                caption_entities=[e.to_dict() for e in chunk.caption_entities] or None,
            )
        elif chunk.content_type == ContentType.FILE:
            if (
                chunk.file_name != None
                and (
                    chunk.file_name.endswith(".md") or chunk.file_name.endswith(".txt")
                )
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
    return True
