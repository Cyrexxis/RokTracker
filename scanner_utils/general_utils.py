import string
import random


def to_int_check(element):
    try:
        return int(element)
    except ValueError:
        # return element
        return int(0)


def is_string_int(element: str) -> bool:
    try:
        _ = int(element)
        return True
    except ValueError:
        return False


def is_string_float(element: str) -> bool:
    try:
        _ = float(element)
        return True
    except ValueError:
        return False


def generate_random_id(length):
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def next_alpha(s):
    return chr((ord(s.upper()) + 1 - 65) % 26 + 65)


def random_delay() -> float:
    return random.random() * 0.1


def format_timedelta_to_HHMMSS(td):
    td_in_seconds = td.total_seconds()
    hours, remainder = divmod(td_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    if minutes < 10:
        minutes = "0{}".format(minutes)
    if seconds < 10:
        seconds = "0{}".format(seconds)
    return "{}:{}:{}".format(hours, minutes, seconds)
