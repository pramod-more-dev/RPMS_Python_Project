
import re


def is_valid_email(email: str) -> bool:
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(email and re.fullmatch(pattern, email))


def is_valid_mobile(mobile: str) -> bool:
    return bool(mobile and re.fullmatch(r"\d{10}", mobile))


def is_valid_percentage(value: float) -> bool:
    return 0 <= value <= 100


def is_valid_backlog_count(value: int) -> bool:
    return value >= 0


def is_valid_passing_year(value: int) -> bool:
    return 2000 <= value <= 2100


def is_valid_package(value: float) -> bool:
    return value >= 0


def is_valid_openings(value: int) -> bool:
    return value > 0
