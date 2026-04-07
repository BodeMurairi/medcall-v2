#!/usr/bin/env python3

from sqlalchemy.orm import Session
from database.session import get_db
from models.database_models import PatientRegistration, Consultation
from .normalize_phone import normalize_phone_number

def get_patient_id(phone_number:str)->int:
    """
    get patient id
    Args:
        phone_number:str
        return patient_id:int
    """
    db:Session = next(get_db()) # get session
    phone_number = normalize_phone_number(phone_number=phone_number)
    patient = db.query(PatientRegistration).where(PatientRegistration.phone_number == phone_number).first()
    return patient.id

def get_consultation_id(patient_id:int, phone_number:str)->tuple[str, dict[int,str]]:
    """
    get consultation id
    Args
        patient_id:int
        phone_number:str
        return tuple(patient_id:int, consultation_id:int
    """
    patient = get_patient_id(phone_number=phone_number)
    db:Session = next(get_db())
    consultation = db.query(Consultation).where(Consultation.patient_id == patient).all()
    current_consultation = consultation[-1]
    consultation_ids = {
        "consultion_system_id":current_consultation.id,
        "consultation_thread":current_consultation.consultation_id
    }
    return patient, consultation_ids
