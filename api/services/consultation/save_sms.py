#!/usr/bin/env python3

from datetime import datetime
from sqlalchemy.orm import Session
from models.database_models import ConsultationSMS, Consultation
from database.session import get_db

def save_consultation_sms(
    db: Session,
    consultation_id: int,
    message_type: str,
    content: str,
    sms_metadata: str = None  # Already a JSON string or None — do not re-serialize
):
    """Save a single SMS message to a consultation."""
    sms = ConsultationSMS(
        consultation_id=consultation_id,
        message_type=message_type,
        content=content,
        sms_metadata=sms_metadata,
        timestamp=datetime.utcnow()
    )
    try:
        db.add(sms)
        db.commit()
        db.refresh(sms)
        return sms
    except Exception as error:
        print(f"Error:\n{error}")
        return
