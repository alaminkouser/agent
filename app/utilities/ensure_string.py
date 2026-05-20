def ensure_string(data) -> bool:
    if isinstance(data, bytes):
        try:
            data.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
    elif isinstance(data, str):
        return True
    return False
