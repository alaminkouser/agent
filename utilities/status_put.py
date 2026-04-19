import subprocess


def status_put(status: str):
    """
    I can help you to update website status. You need to provide status in string format.
    The string needs to be in single line. The status is shown in https://alaminkouser.com/status/
    """

    try:
        subprocess.run(["status-put", status], check=True)
        return "Status updated successfully"
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"
