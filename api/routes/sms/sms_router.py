#!/usr/bin/env python3

import datetime
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from schemas.sms_schema import InboundSMS
from database.session import get_db
from controllers.sms.sms_controller import inbound_sms

router = APIRouter(
    prefix="/sms",
    tags=["Sends consultation sms"]
)

@router.post("/inbound")
async def receive_sms(request: Request, db: Session = Depends(get_db)):
    """Endpoint to receive inbound SMS messages from SMSGateway24 (form-encoded)."""
    form = await request.form()
    sms = InboundSMS.model_validate(dict(form))
    return await inbound_sms(db=db, payload=sms)

@router.post("/delivery_status")
async def delivery_status(request: Request):
    """
    Endpoint to receive delivery status updates from
    the SMS provider.
    """
    payload = dict(await request.form())
    return {
        "sms_id": payload.get("sms_id"),
        "status": payload.get("status_message"),
        "timestamp": str(datetime.datetime.now())
    }
