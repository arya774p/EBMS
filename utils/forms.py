from datetime import date
from decimal import Decimal, InvalidOperation


def clean_text(value):
    return (value or "").strip()


def optional_text(value):
    value = clean_text(value)
    return value or None


def parse_decimal(value, field_name, minimum=None):
    try:
        parsed = Decimal(clean_text(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_name} must be a valid number.")

    if minimum is not None and parsed < Decimal(str(minimum)):
        raise ValueError(f"{field_name} must be at least {minimum}.")

    return parsed.quantize(Decimal("0.01"))


def parse_date(value, field_name):
    try:
        return date.fromisoformat(clean_text(value))
    except ValueError:
        raise ValueError(f"{field_name} must be a valid date.")


def validate_phone(phone):
    phone = clean_text(phone)
    if not phone.isdigit() or not 10 <= len(phone) <= 15:
        raise ValueError("Phone must contain 10 to 15 digits.")
    return phone


def validate_pincode(pincode):
    pincode = clean_text(pincode)
    if not pincode.isdigit() or len(pincode) != 6:
        raise ValueError("Pincode must contain exactly 6 digits.")
    return pincode
