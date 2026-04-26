#!/usr/bin/env python3

import os
import threading
import africastalking
from dotenv import load_dotenv

load_dotenv()


def _send(phone_number: str, message: str):
    try:
        africastalking.initialize(
            username=os.getenv("AFRICAUSERNAME", "sandbox"),
            api_key=os.getenv("AFRICAS_API_KEY", ""),
        )
        sms = africastalking.SMS
        response = sms.send(message, [phone_number])
        print(f"SMS sent to {phone_number}: {response}")
    except Exception as e:
        print(f"SMS send error to {phone_number}: {e}")


def send_sms(phone_number: str, message: str):
    """Fire-and-forget SMS — runs in a daemon thread so it never blocks USSD."""
    threading.Thread(target=_send, args=(phone_number, message), daemon=True).start()
