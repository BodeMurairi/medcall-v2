#!/usr/bin/env python3

import africastalking
from config.settings import africas_config


def _get_sms_client():
    africastalking.initialize(
        username=africas_config["username"],
        api_key=africas_config["AFRICAS_API_KEY"]
    )
    return africastalking.SMS


def send_sms_notification(phone_number: str, message: str) -> bool:
    """
    Send an outbound SMS to the patient via Africa's Talking.
    Returns True on success, False on failure.
    """
    try:
        sms = _get_sms_client()
        sender = africas_config.get("channels")
        response = sms.send(message, [phone_number], sender)
        print(f"[INFO] SMS sent to {phone_number}: {response}")
        return True
    except Exception as e:
        print(f"[ERROR] SMS notification failed for {phone_number}: {e}")
        return False
