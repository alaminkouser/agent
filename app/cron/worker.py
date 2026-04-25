import os
from pathlib import Path
from datetime import datetime
import time

from pydantic.dataclasses import dataclass
from pydantic_ai.messages import ModelResponsePart
from telegramify_markdown import telegramify, ContentType

from agents.main import agent_main

cron_directory = (
    Path(Path(__file__).resolve().parent)
    .joinpath("..", "..", ".DATA", "cron")
    .resolve()
)

cron_directory.mkdir(parents=True, exist_ok=True)


@dataclass
class Buffer:
    type: ModelResponsePart | None
    text: str


async def cron_worker(telegram_app):
    while True:
        for cron_file in cron_directory.iterdir():
            file_date_time_str = cron_file.name.split(".")[0]
            file_date_time = datetime.strptime(file_date_time_str, "%Y-%m-%d_%H-%M-%S")
            if file_date_time < datetime.now():

                try:
                    agent = agent_main()
                    agent_run = await agent.run(cron_file.read_text())
                    chunk_list = await telegramify(
                        agent_run.output, max_message_length=4096
                    )
                    for chunk in chunk_list:
                        if chunk.content_type == ContentType.TEXT:
                            await telegram_app.bot.send_message(
                                chat_id=int(os.getenv("TELEGRAM_CHAT_ID")),
                                text=chunk.text,
                            )
                        elif chunk.content_type == ContentType.PHOTO:
                            await telegram_app.bot.send_photo(
                                chat_id=int(os.getenv("TELEGRAM_CHAT_ID")),
                                photo=chunk.file_data,
                                caption=chunk.caption_text or None,
                            )
                        elif chunk.content_type == ContentType.FILE:
                            await telegram_app.bot.send_document(
                                chat_id=int(os.getenv("TELEGRAM_CHAT_ID")),
                                document=chunk.file_data,
                                filename=chunk.file_name,
                            )

                    cron_file.unlink()

                except Exception as e:
                    print(e)
                    await telegram_app.bot.send_message(
                        chat_id=int(os.getenv("TELEGRAM_CHAT_ID")), text=str(e)
                    )

        time.sleep(10)
