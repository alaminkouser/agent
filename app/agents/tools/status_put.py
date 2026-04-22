from pydantic.dataclasses import dataclass
import subprocess


@dataclass
class StatusPutInput:
    status: str


@dataclass
class StatusPutOutput:
    ok: bool


def status_put(input: StatusPutInput) -> StatusPutOutput:
    """
    This function runs status-put cli script to update website status.
    """
    try:
        subprocess.run(["status-put", input.status])
        return StatusPutOutput(ok=True)
    except Exception as e:
        print(e)
        return StatusPutOutput(ok=False)
