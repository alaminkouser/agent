import os
from pathlib import Path
from datetime import datetime
import time

from pydantic.dataclasses import dataclass
from pydantic_ai.messages import ModelResponsePart
from telegram import Update

from utilities.send_message import send_message
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
                print(cron_file.read_text())

                try:
                    agent = agent_main()
                    agent_run = await agent.run(cron_file.read_text())
                    await telegram_app.bot.send_message(
                        chat_id=int(os.getenv("TELEGRAM_CHAT_ID")),
                        text=agent_run.output,
                    )
                    cron_file.unlink()

                except Exception as e:
                    print(e)
                    await telegram_app.bot.send_message(
                        chat_id=int(os.getenv("TELEGRAM_CHAT_ID")), text=str(e)
                    )

            else:
                print("NOT YET")

        time.sleep(10)
