from pydantic import BaseModel
import subprocess


class StatusPutInput(BaseModel):
    status: str


class StatusPutOutput(BaseModel):
    ok: bool


def tool_status_put(input: StatusPutInput) -> StatusPutOutput:
    """
    This function runs status-put cli script to update website status.
    """
    try:
        subprocess.run(["status-put", input.status])
        return StatusPutOutput(ok=True)
    except Exception as e:
        print(e)
        return StatusPutOutput(ok=False)
