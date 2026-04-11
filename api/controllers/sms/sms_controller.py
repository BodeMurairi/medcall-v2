#!/usr/bin/env python3

import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from services.consultation.consultation_management import handle_consultation
from services.sms.sms_checker import filter_sender_sms
from services.sms.send_sms import send_sms

async def inbound_sms(db:Session, payload):
    """
    This controller manages the processing of inbound SMS messages.
    It checks the content of the SMS,
    """
    # collect sms payload details
    sender = payload.phoneNumber
    text = payload.message
    thread_id = str(uuid.uuid4()).split("-")[2]
    check_user_sms = filter_sender_sms(phone_number=sender, message=text)

    if not check_user_sms:
        raise HTTPException(status_code=400, detail="SMS content did not meet processing criteria.")

    response = handle_consultation(db=db, phone_number=sender, user_input=text, thread_id=thread_id)
    doctor_response = response.get("message") or "Sorry, your message was received but could not be processed at the moment."
    sms_response = send_sms(to=sender, message=doctor_response)
    return sms_response
