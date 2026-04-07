#!/usr/bin/env python3

from sqlalchemy.orm import Session
from models.database_models import PatientRegistration, PatientMedicalInfo, PatientPersonalInfo
from database.session import get_db

from langchain.tools import tool
from external_integration.agents.utils.convert_to_dict import to_dict
from external_integration.agents.utils.normalize_phone import normalize_phone_number

@tool
def verify_registration(phone_number:str):
    """
    This tool verify if a user is registered within MedCall.
    Arg:
        phone_number:str : User phone number
        db:Session the sqlalchemy session
        return True if user registered or False if user not registered
    """
    normalized_number = normalize_phone_number(phone_number=phone_number)
    db:Session = next(get_db())
    patient = db.query(PatientRegistration).where(PatientRegistration.phone_number == normalized_number).first()
    return {"registered": bool(patient)}

@tool
def collect_user_personal_info(phone_number:str):
    """
    This tool collects user personal information
    Args:
        phone_number:str : User phone number
        db:Session: Sqlalchemy session
        return [personal information] or None if unavailable
    """
    normalized_number = normalize_phone_number(phone_number=phone_number)
    db:Session = next(get_db())
    patient = db.query(
        PatientRegistration
        ).where(
            PatientRegistration.phone_number == normalized_number
            ).first()
    if not patient:
        return None
    personal_information = db.query(
        PatientPersonalInfo
        ).where(
            PatientPersonalInfo.patient_id == patient.id
            ).first()
    return to_dict(personal_information)

@tool
def collect_medical_information(phone_number:str):
    """
    This tool collects user personal information
    Args:
        phone_number:str : User phone number
        db:Session: Sqlalchemy session
        return [personal information] or None if unavailable
    """
    normalized_number = normalize_phone_number(phone_number=phone_number)
    db:Session = next(get_db())
    patient = db.query(
        PatientRegistration
        ).where(
            PatientRegistration.phone_number == normalized_number
            ).first()
    if not patient:
        return None
    medical_information = db.query(
        PatientMedicalInfo
        ).where(
            PatientMedicalInfo.patient_id == patient.id
            ).first()
    return to_dict(medical_information)
