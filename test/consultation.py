#!/usr/bin/env python3

import requests

def test_consultation():
    url = "http://localhost:8000/consultation"
    payload = {
        "phone_number": "+250795020998",
        "message": "No that's all",
        "thread_id": "7fee659a"
        }
    response = requests.post(url=url, json=payload)
    response.raise_for_status()
    print(f"Response:\n {response.json()}")

if __name__ == "__main__":
    test_consultation()
