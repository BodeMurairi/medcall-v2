#!/usr/bin/env python3

import bcrypt
from datetime import datetime
from sqlalchemy.orm import Session
from models.database_models import PatientRegistration, Consultation
from database.session import get_db
from services.ussd.response import con, end
from services.ussd.state import ViewConsultation
from utils.helpers import search_user, search_list_patient_data

def view_consultation(session, user_input, db:Session):
    """View patient consultation, sms, referral"""
    user_input = user_input.strip()
    state = session["state"]
    phone_number = session["phone"]

    existing_user = search_user(db=db,
                                phone_number=phone_number,
                                model=PatientRegistration
                                )
    
    if state == ViewConsultation.VERIFY_PIN:
        session["pin"] = user_input
        session["patient_id"] = existing_user.id
        if not bcrypt.checkpw(
            session["pin"].encode("utf-8"),
            existing_user.pin.encode("utf-8")
            ):
            return end("Incorrect PIN. Try again later")
    
    patient_data = search_list_patient_data(db=db,
                                       model=Consultation,
                                       patient_id=session["patient_id"])
    
    if not patient_data:
        return end("No Data available")
    
    patient_data = patient_data[:2]
    
    return [
        {"consultation_date":consultation.start_time,
         "consultation_summary":consultation.consultation_summary} 
         for consultation in patient_data
         ]
