#!/usr/bin/env python3

import bcrypt
from sqlalchemy.orm import Session
from datetime import datetime

from models.database_models import PatientRegistration, PatientMedicalInfo
from schemas.users import PatientMedicalInformation as medical_info_schema
from services.ussd.response import con, end
from services.ussd.state import USSDMedicalInfo, ViewInfo
from utils.blood_type import blood_type
from utils.orm_to_dict import dict_medical_info
from utils.helpers import search_patient_data

_BACK_HINT = "\n0. Back"


def _go_back(session):
    from services.ussd.flows.menu_flow import medical_info_submenu
    for key in ["blood_type", "allergies", "chronic_illness", "recent_vaccination"]:
        session.pop(key, None)
    return medical_info_submenu(session)


def _get_patient(db, phone_number):
    return db.query(PatientRegistration).where(
        PatientRegistration.phone_number == phone_number
    ).first()


def save_medical_info(session, user_input, db: Session):

    user_input = user_input.strip()
    state = session["state"]
    phone_number = session["phone"]

    if user_input == "0":
        return _go_back(session)

    patient = _get_patient(db, phone_number)
    if not patient:
        return end("Not registered. Redial and choose Register.")

    if state == USSDMedicalInfo.VERIFY_PIN:
        if not bcrypt.checkpw(user_input.encode("utf-8"), patient.pin.encode("utf-8")):
            return end("Incorrect PIN. Please redial.")
        session["patient_id"] = patient.id
        session["state"] = USSDMedicalInfo.BLOOD_TYPE
        return con(f"Blood type? Options: {blood_type()}" + _BACK_HINT)

    if state == USSDMedicalInfo.BLOOD_TYPE:
        session["blood_type"] = user_input.upper()
        session["state"] = USSDMedicalInfo.ALLERGIES
        return con("List your allergies (or 'none')" + _BACK_HINT)

    if state == USSDMedicalInfo.ALLERGIES:
        session["allergies"] = user_input.upper()
        session["state"] = USSDMedicalInfo.CHRONIC_ILLNESS
        return con("List chronic illnesses (or 'none')" + _BACK_HINT)

    if state == USSDMedicalInfo.CHRONIC_ILLNESS:
        session["chronic_illness"] = user_input.upper()
        session["state"] = USSDMedicalInfo.RECENT_VACCINATION
        return con("Recent vaccinations (or 'none')" + _BACK_HINT)

    if state == USSDMedicalInfo.RECENT_VACCINATION:
        session["recent_vaccination"] = user_input.upper()

        details = {
            "blood_type": session["blood_type"],
            "allergies": session["allergies"],
            "chronic_illness": session["chronic_illness"],
            "recent_vaccination": session["recent_vaccination"],
        }

        try:
            validated = medical_info_schema(**details)
        except Exception:
            return end("Invalid data. Please redial and try again.")

        try:
            new_record = PatientMedicalInfo(
                **validated.model_dump(mode="json"),
                patient_id=session["patient_id"],
                updated_at=datetime.utcnow(),
            )
            db.add(new_record)
            db.commit()
            db.refresh(new_record)
        except Exception as e:
            print(f"Medical info DB error: {e}")
            return end("Save failed. Please try again later.")

        return end(
            f"Medical info saved for {patient.first_name} {patient.last_name}.\n"
            "Redial to view or update."
        )

    return end("Unexpected state. Please redial.")


def view_medical_info(session, user_input, db: Session):

    user_input = user_input.strip()
    state = session["state"]
    phone_number = session["phone"]

    if user_input == "0":
        return _go_back(session)

    patient = _get_patient(db, phone_number)
    if not patient:
        return end("Not registered. Redial and choose Register.")

    if state == ViewInfo.VERIFY_PIN:
        if not bcrypt.checkpw(user_input.encode("utf-8"), patient.pin.encode("utf-8")):
            return end("Incorrect PIN. Please redial.")

        session["patient_id"] = patient.id

        medical_info = search_patient_data(
            db=db, model=PatientMedicalInfo, patient_id=session["patient_id"]
        ).first()

        if not medical_info:
            return end("No medical info on file. Redial and choose Update.")

        d = dict_medical_info(model=medical_info)
        return end(
            f"{patient.first_name} {patient.last_name}\n"
            f"Blood Type: {d['blood_type']}\n"
            f"Allergies: {d['allergies'] or 'None'}\n"
            f"Chronic Illness: {d['chronic_illness'] or 'None'}\n"
            f"Vaccinations: {d['recent_vaccination'] or 'None'}"
        )

    return end("Unexpected state. Please redial.")
