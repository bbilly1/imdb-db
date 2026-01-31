"""helper function"""

def int_or_none(value: str) -> int | None:
    """convert str to int or None"""
    if value == "\\N":
        return None

    if value.isdigit():
        return int(value)

    raise ValueError(f"failed to convert to int or none: {value}")


def bool_match(value: str) -> bool:
    """convert str "1" | "0" to bool"""
    if value == "1":
        return True

    if value == "0":
        return False

    raise ValueError(f"failed to convert to bool: {value}")


def list_of_str_or_none(value: str) -> list[str] | None:
    """comma separated list of string or none"""
    if value == "\\N":
        return None

    return value.split(",")
