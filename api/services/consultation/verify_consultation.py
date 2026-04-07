#!/usr/bin/env python3

from external_integration.agents.tools.consultation_tool import verify_registration

def check_user(phone_number:str):
    """this function manually runs verify registration toos"""
    result = verify_registration.invoke({"phone_number": phone_number})
    if not result.get("registered", False):
        return {
            "status": "complete",
            "register":False,
            "current_message": "Sorry! You are not registered. Please use *384*41992# to register.",
            "tool_call": {},
            "consultation_sms": [],
            "doctor_questions": [],
            "patient_responses": [],
            "collected_data": {},
            "summary": "User not registered"
            }
    return {
        "status":"in_progress",
        "register":True
        }
