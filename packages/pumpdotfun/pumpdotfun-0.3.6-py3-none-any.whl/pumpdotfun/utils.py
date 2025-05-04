import math
import time
from consts import (PF_CMD_CLI, PF_CLI)

# Constants (you'll need to define LOG_CHANNEL and console accordingly)

def is_number(input_text: str | None) -> bool:
    if input_text is None:
        return False
    try:
        num = float(input_text)
        return math.isfinite(num)
    except ValueError:
        return False

def shorten_address(address: str, start: int, end: int) -> str | None:
    try:
        first_part = address[:start]
        last_part = address[-end:]
        return f"{first_part}...{last_part}"
    except Exception:
        return None

def log(message: str) -> None:
    if message:
        PF_CLI.send_message(PF_CMD_CLI, message)

def sleep(ms: int) -> None:
    time.sleep(ms / 1000)
