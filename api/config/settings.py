#!/usr/bin/env python3

import os
from dotenv import load_dotenv

load_dotenv()

africas_config = {
    "channels": os.getenv("africastalking_channel"),
    "AFRICAS_API_KEY": os.getenv("AFRICAS_API_KEY"),
    "username": os.getenv("AFRICAUSERNAME")
}

sms_config = {
    "GATEWAY_TOKEN": os.getenv("SMS_API_TOKEN"),
    "DEVICE_ID": os.getenv("SMS_DEVICE_ID")
}
