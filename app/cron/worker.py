import os
import asyncio
from pathlib import Path
from datetime import datetime

from telegram import MessageEntity
from telegramify_markdown import Text, Photo, File
from pydantic import BaseModel
from pydantic_ai import UsageLimits
from pydantic_ai.messages import (
    ModelResponsePart,
    ThinkingPart,
    ToolCallPart,
    PartStartEvent,
    PartDeltaEvent,
    PartEndEvent,
    TextPart,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    FinalResultEvent,
)
from pydantic_ai.run import AgentRunResultEvent
from telegramify_markdown import telegramify

from agents.cron import agent_cron

cron_directory = (
    Path(Path(__file__).resolve().parent)
    .joinpath("..", "..", ".DATA", "cron")
    .resolve()
)


class Buffer(BaseModel):
    type: ModelResponsePart | None
    text: str


async def cron_worker(telegram_app):

    async def send_message(text_message: str):
        chunk_list = await telegramify(text_message, max_message_length=4096)
        chat_id = int(os.getenv("TELEGRAM_CHAT_ID", ""))

        for chunk in chunk_list:
            if isinstance(chunk, Text):
                ptb_entities = (
                    MessageEntity.de_list(
                        [e.to_dict() for e in chunk.entities], bot=None
                    )
                    if chunk.entities
                    else None
                )

                await telegram_app.bot.send_message(
                    chat_id=chat_id,
                    text=chunk.text,
                    entities=ptb_entities,
                )

            elif isinstance(chunk, Photo):
                ptb_caption_entities = (
                    MessageEntity.de_list(
                        [e.to_dict() for e in chunk.caption_entities], bot=None
                    )
                    if chunk.caption_entities
                    else None
                )

                await telegram_app.bot.send_photo(
                    chat_id=chat_id,
                    photo=chunk.file_data,
                    filename=chunk.file_name,
                    caption=chunk.caption_text or None,
                    caption_entities=ptb_caption_entities,
                )

            elif isinstance(chunk, File):
                ptb_caption_entities = (
                    MessageEntity.de_list(
                        [e.to_dict() for e in chunk.caption_entities], bot=None
                    )
                    if chunk.caption_entities
                    else None
                )

                await telegram_app.bot.send_document(
                    chat_id=chat_id,
                    document=chunk.file_data,
                    filename=chunk.file_name,
                    caption=chunk.caption_text or None,
                    caption_entities=ptb_caption_entities,
                )

    while True:
        for cron_file in cron_directory.iterdir():
            file_date_time_str = cron_file.name.split(".")[0]
            file_date_time = datetime.strptime(file_date_time_str, "%Y-%m-%d_%H-%M-%S")
            if file_date_time < datetime.now():

                try:
                    agent = agent_cron()
                    cron_task_text = cron_file.read_text()
                    await send_message(f"# CRON\n\n{cron_task_text}")

                    buffer = Buffer(
                        type=None,
                        text="",
                    )

                    async for event in agent.run_stream_events(
                        cron_task_text, usage_limits=UsageLimits(tool_calls_limit=25)
                    ):

                        # --- START ---
                        if isinstance(event, PartStartEvent):
                            text = ""
                            if isinstance(event.part, ToolCallPart):
                                text = event.part.tool_name
                            elif isinstance(event.part, TextPart):
                                text = event.part.content

                            buffer.type = type(event.part)
                            buffer.text = text

                        # --- DELTA ---
                        elif isinstance(event, PartDeltaEvent):
                            buffer.text += event.delta.content_delta

                        # --- END (THIS IS WHERE YOU PRINT) ---
                        elif isinstance(event, PartEndEvent):

                            if buffer.type is ThinkingPart:
                                await send_message(f"# THINKING\n\n{buffer.text}")

                            elif buffer.type is TextPart:
                                await send_message(f"{buffer.text}")

                            elif buffer.type is ToolCallPart:
                                await send_message(f"# TOOL\n\n{buffer.text}")

                            else:
                                await send_message("UNKNOWN PART")

                        else:
                            ignore_events = (
                                FunctionToolCallEvent,
                                FunctionToolResultEvent,
                                FinalResultEvent,
                                AgentRunResultEvent,
                            )
                            if not isinstance(event, ignore_events):
                                await send_message(f"UNKNOWN EVENT: {event}")

                    cron_file.unlink()

                except Exception as e:
                    print(e)
                    await telegram_app.bot.send_message(
                        chat_id=int(os.getenv("TELEGRAM_CHAT_ID", "")), text=str(e)
                    )

        await asyncio.sleep(10)
