#!/usr/bin/env python3

import bcrypt
from sqlalchemy.orm import Session
from datetime import datetime

from models.database_models import PatientRegistration, PatientPersonalInfo
from schemas.users import PatientPersonalInfo as patient_schema
from services.ussd.response import con, end
from services.ussd.state import USSDPersonalInfo, ViewPersonalInfo
from utils.orm_to_dict import dict_personal_info
from utils.helpers import search_patient_data

_BACK_HINT = "\n0. Back"


def _go_back(session):
    from services.ussd.flows.menu_flow import personal_info_submenu
    for key in ["age", "gender", "nationality", "country_residence",
                "city_of_residence", "address", "next_kin",
                "relationship", "kin_phone_number", "preferred_language"]:
        session.pop(key, None)
    return personal_info_submenu(session)


def _get_patient(db, phone_number):
    return db.query(PatientRegistration).where(
        PatientRegistration.phone_number == phone_number
    ).first()


def complete_personal_info_flow(session, user_input, db: Session):

    user_input = user_input.strip()
    state = session["state"]
    phone_number = session["phone"]

    if user_input == "0":
        return _go_back(session)

    patient = _get_patient(db, phone_number)
    if not patient:
        return end("Not registered. Redial and choose Register.")

    if state == USSDPersonalInfo.VERIFY_PIN:
        if not bcrypt.checkpw(user_input.encode("utf-8"), patient.pin.encode("utf-8")):
            return end("Incorrect PIN. Please redial.")
        session["patient_id"] = patient.id
        session["state"] = USSDPersonalInfo.COMPLETE_AGE
        return con("Enter your age" + _BACK_HINT)

    if state == USSDPersonalInfo.COMPLETE_AGE:
        try:
            session["age"] = int(user_input)
        except ValueError:
            return con("Please enter a valid age (numbers only)" + _BACK_HINT)
        session["state"] = USSDPersonalInfo.COMPLETE_GENDER
        return con("Gender: M for Male, F for Female" + _BACK_HINT)

    if state == USSDPersonalInfo.COMPLETE_GENDER:
        session["gender"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_NATIONALITY
        return con("Enter your nationality" + _BACK_HINT)

    if state == USSDPersonalInfo.COMPLETE_NATIONALITY:
        session["nationality"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_COUNTRY_OF_RESIDENCE
        return con("Country of residence" + _BACK_HINT)

    if state == USSDPersonalInfo.COMPLETE_COUNTRY_OF_RESIDENCE:
        session["country_residence"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_CITY_OF_RESIDENCE
        return con("City of residence" + _BACK_HINT)

    if state == USSDPersonalInfo.COMPLETE_CITY_OF_RESIDENCE:
        session["city_of_residence"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_ADDRESS
        return con("Full home address" + _BACK_HINT)

    if state == USSDPersonalInfo.COMPLETE_ADDRESS:
        session["address"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_NEXT_KIN
        return con("Next of kin name (emergency contact)" + _BACK_HINT)

    if state == USSDPersonalInfo.COMPLETE_NEXT_KIN:
        session["next_kin"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_NEXT_KIN_RELATIONSHIP
        return con("Relationship to next of kin\neg. Brother, Sister, Father" + _BACK_HINT)

    if state == USSDPersonalInfo.COMPLETE_NEXT_KIN_RELATIONSHIP:
        session["relationship"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_NEXT_KIN_PHONE_NUMBER
        return con("Next of kin phone number" + _BACK_HINT)

    if state == USSDPersonalInfo.COMPLETE_NEXT_KIN_PHONE_NUMBER:
        session["kin_phone_number"] = user_input
        session["state"] = USSDPersonalInfo.COMPLETE_PREFERRED_LANGUAGE
        return con("Preferred language\neg. English, French, Swahili" + _BACK_HINT)

    if state == USSDPersonalInfo.COMPLETE_PREFERRED_LANGUAGE:
        session["preferred_language"] = user_input.upper()

        details = {
            "age": session["age"],
            "gender": session["gender"],
            "nationality": session["nationality"],
            "country_of_residence": session["country_residence"],
            "city_of_residence": session["city_of_residence"],
            "address": session["address"],
            "next_of_kin": session["next_kin"],
            "next_of_kin_phone_number": session["kin_phone_number"],
            "patient_next_relationship": session["relationship"],
            "preferred_language": session["preferred_language"],
        }

        try:
            validated = patient_schema(**details)
        except Exception:
            return end("Invalid data. Please redial and try again.")

        try:
            personal_info = PatientPersonalInfo(
                **validated.model_dump(mode="json"),
                patient_id=session["patient_id"],
                updated_at=datetime.utcnow(),
            )
            db.add(personal_info)
            db.commit()
            db.refresh(personal_info)
        except Exception as e:
            print(f"Personal info DB error: {e}")
            return end("Save failed. Please try again later.")

        return end(
            f"Personal info saved for {patient.first_name} {patient.last_name}.\n"
            "Redial to view or update."
        )

    return end("Unexpected state. Please redial.")


def view_personal_info(session, user_input, db: Session):

    user_input = user_input.strip()
    state = session["state"]
    phone_number = session["phone"]

    if user_input == "0":
        return _go_back(session)

    patient = _get_patient(db, phone_number)
    if not patient:
        return end("Not registered. Redial and choose Register.")

    if state == ViewPersonalInfo.VERIFY_PIN:
        if not bcrypt.checkpw(user_input.encode("utf-8"), patient.pin.encode("utf-8")):
            return end("Incorrect PIN. Please redial.")

        session["patient_id"] = patient.id

        personal_data = search_patient_data(
            db=db, model=PatientPersonalInfo, patient_id=session["patient_id"]
        ).first()

        if not personal_data:
            return end("No personal info on file. Redial and choose Update.")

        d = dict_personal_info(model=personal_data)
        return end(
            f"{patient.first_name} {patient.last_name}\n"
            f"Age: {d['age']} | Gender: {d['gender']}\n"
            f"Country: {d['country_of_residence']}\n"
            f"City: {d['city_of_residence']}\n"
            f"Language: {d['preferred_language']}\n"
            f"Next of kin: {d['next_of_kin']} ({d['patient_next_relationship']})"
        )

    return end("Unexpected state. Please redial.")
