#!/usr/bin/env python3

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat


def normalize_phone_number(phone_number: str, default_region: str = "RW") -> str:
    """
    Normalize any phone number to E.164 format.

    Args:
        phone_number (str): Input number (any format)
        default_region (str): Fallback country code (e.g. "RW", "US", "KE")

    Returns:
        str: Normalized phone number (E.164 format, e.g. +250795020998)

    Raises:
        ValueError: If number is invalid
    """

    if not phone_number:
        raise ValueError("Phone number is required")

    try:
        parsed_number = phonenumbers.parse(phone_number, default_region)

        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError(f"Invalid phone number: {phone_number}")

        return phonenumbers.format_number(
            parsed_number,
            PhoneNumberFormat.E164
        )

    except NumberParseException as e:
        raise ValueError(f"Error parsing phone number: {phone_number}") from e
