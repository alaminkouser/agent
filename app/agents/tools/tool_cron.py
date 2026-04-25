from pydantic.dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import uuid


@dataclass
class CronCreateInput:
    time: datetime
    task: str


cron_directory = (
    Path(Path(__file__).resolve().parent)
    .joinpath("..", "..", "..", ".DATA", "cron")
    .resolve()
)

cron_directory.mkdir(parents=True, exist_ok=True)


def tool_cron_create(input: CronCreateInput) -> str:
    """
    Use this tool to create a cron job. If you need to run a task at a specific
    time, use this tool to create a cron job.
    """
    uuid_str = str(uuid.uuid4())
    id = uuid_str.replace("-", "")[:12] + uuid_str.replace("-", "")[13:]
    cron_file = cron_directory.joinpath(
        input.time.strftime("%Y-%m-%d_%H-%M-%S") + "." + id + ".txt"
    )
    cron_file.write_text(input.task)
    return f"Cron job created for {input.time} with id {id}"
