#!/usr/bin/env python3

import logging
import requests
from config.settings import sms_config

if all(value is None for value in sms_config.values()):
    raise ValueError("SMS API configuration is missing. Please set the required environment variables.")

def send_sms(to:str, message:str):
    """
    This function sends SMS via SMS Gateway24 API
    Args:
        to (str): The recipient's phone number.
        message (str): The content of the SMS message.
    """
    url = "https://smsgateway24.com/getdata/addsms"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload_data = {
        "token": sms_config["GATEWAY_TOKEN"],
        "sendto": to,
        "body": message,
        "device_id": sms_config["DEVICE_ID"],
        "sim": 0
    }
    response = requests.post(
        url=url,
        headers=headers,
        data=payload_data
    )
    logging.warning("SEND SMS | to=%s | status=%s | response=%s", to, response.status_code, response.text[:200])
    if not response.status_code == 200:
        return {"success": False,
                "message": f"Failed to send SMS: {response.text}"
                }
    return {"success":True,
            "response": response.json()
            }
