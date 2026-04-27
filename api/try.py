#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def try_requests():
    url = "https://smsgateway24.com/getdata/addsms"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "token": os.getenv("SMS_API_TOKEN"),
        "device_id": os.getenv("SMS_DEVICE_ID"),
        "sendto":"+250727484499",
        "body":"Hello from MedCall API! This is a test message.",
        "sim":0
    }
    response = requests.post(url, headers=headers, data=params)
    response.raise_for_status()
    print("SMS sent successfully:", response.json())

try_requests()
