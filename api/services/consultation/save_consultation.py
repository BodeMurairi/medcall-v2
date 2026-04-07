#!/usr/bin/env python3

from datetime import datetime
from sqlalchemy.orm import Session
from database.session import get_db
from models.database_models import ConsultationSMS, Consultation

def save_consultation(
        db:Session,
        patient_id:int,
        risk_level,
        consultation_summary:str,
        consultation_status:bool,
        thread_id:str
        ):
    """This function save a new consultation inside the db"""
    consultation = Consultation(
        patient_id = patient_id,
        risk_level = risk_level,
        consultation_summary = consultation_summary,
        consultation_status = consultation_status,
        thread_id=thread_id
        )
    try:
        db.add(consultation)
        db.commit()
        db.refresh(consultation)
        return consultation
    except Exception as error:
        print(f"Error\n:{error}")
        return
