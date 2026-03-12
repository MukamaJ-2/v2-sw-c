from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

from evoting.domain.constants import MIN_PASSWORD_LENGTH


class ValidationError(ValueError):
    """Raised when user-provided data violates a domain rule."""


@dataclass(frozen=True)
class AgeCalculation:
    birth_date: datetime
    age: int


def ensure_non_empty(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{field_name} cannot be empty.")
    return cleaned


def parse_date(value: str, field_name: str = "Date") -> datetime:
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d")
    except ValueError as error:
        raise ValidationError(f"{field_name} must be in YYYY-MM-DD format.") from error


def calculate_age(birth_date: datetime, today: date | None = None) -> int:
    reference = today or datetime.now().date()
    years = reference.year - birth_date.date().year
    has_had_birthday = (reference.month, reference.day) >= (
        birth_date.month,
        birth_date.day,
    )
    return years if has_had_birthday else years - 1


def parse_birth_date_and_age(value: str) -> AgeCalculation:
    birth_date = parse_date(value, "Date of Birth")
    return AgeCalculation(birth_date=birth_date, age=calculate_age(birth_date))


def ensure_minimum_age(age: int, minimum_age: int, entity_name: str) -> None:
    if age < minimum_age:
        raise ValidationError(
            f"{entity_name} must be at least {minimum_age} years old. Current age: {age}"
        )


def ensure_maximum_age(age: int, maximum_age: int, entity_name: str) -> None:
    if age > maximum_age:
        raise ValidationError(
            f"{entity_name} must not be older than {maximum_age}. Current age: {age}"
        )


def ensure_password_length(password: str) -> str:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )
    return password


def ensure_matches(value: str, confirmation: str, message: str) -> None:
    if value != confirmation:
        raise ValidationError(message)


def ensure_in_options(value: str, valid_values: Iterable[str], error_message: str) -> str:
    cleaned = value.strip()
    if cleaned not in valid_values:
        raise ValidationError(error_message)
    return cleaned


def ensure_unique_national_id(records: dict[int, dict], national_id: str, entity_name: str) -> str:
    cleaned = ensure_non_empty(national_id, "National ID")
    if any(record.get("national_id") == cleaned for record in records.values()):
        raise ValidationError(f"A {entity_name} with this National ID already exists.")
    return cleaned


def parse_positive_int(value: str, field_name: str) -> int:
    try:
        parsed = int(value.strip())
    except ValueError as error:
        raise ValidationError(f"Invalid {field_name.lower()}.") from error
    if parsed <= 0:
        raise ValidationError(f"{field_name} must be positive.")
    return parsed


def parse_non_negative_int(value: str, field_name: str, default: int = 0) -> int:
    if not value.strip():
        return default
    try:
        parsed = int(value.strip())
    except ValueError as error:
        raise ValidationError(f"Invalid {field_name.lower()}.") from error
    if parsed < 0:
        raise ValidationError(f"{field_name} cannot be negative.")
    return parsed


def parse_int(value: str, field_name: str) -> int:
    try:
        return int(value.strip())
    except ValueError as error:
        raise ValidationError(f"Invalid {field_name.lower()}.") from error


def parse_int_list(value: str, field_name: str) -> list[int]:
    try:
        return [int(part.strip()) for part in value.split(",") if part.strip()]
    except ValueError as error:
        raise ValidationError(f"Invalid {field_name.lower()}.") from error


def yes_no_to_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"yes", "no"}:
        raise ValidationError("Please answer yes or no.")
    return normalized == "yes"
