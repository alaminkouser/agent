def ensure_string(data) -> bool:
    if isinstance(data, bytes):
        return data.decode("utf-8")
    elif isinstance(data, str):
        return data
    else:
        raise TypeError(f"Unsupported type: {type(data)}")
