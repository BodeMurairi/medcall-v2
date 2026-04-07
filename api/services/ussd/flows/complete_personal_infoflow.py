#!/usr/bin/env python3

import bcrypt
from sqlalchemy.orm import Session
from datetime import datetime

from models.database_models import PatientRegistration, PatientPersonalInfo

from schemas.users import PatientPersonalInfo as patient_schema

from database.session import get_db

from services.ussd.response import con, end
from services.ussd.state import USSDPersonalInfo

from utils.orm_to_dict import dict_personal_info
from utils.helpers import search_user, search_patient_data

def complete_personal_info_flow(session, user_input, db:Session):
    """Complete Personal Info"""

    user_input = user_input.strip()
    state = session["state"]
    phone_number = session["phone"]

    existing_user = search_user(db=db, phone_number=phone_number, model=PatientRegistration)
    
    if state == USSDPersonalInfo.VERIFY_PIN:
        session["pin"] = user_input
        session["patient_id"] = existing_user.id
        if not bcrypt.checkpw(
            session["pin"].encode("utf-8"),
            existing_user.pin.encode("utf-8")
            ):
            return end("Incorrect PIN. Try again later")
        session["state"] = USSDPersonalInfo.COMPLETE_AGE
        return con("Enter your Age")
    
    if state == USSDPersonalInfo.COMPLETE_AGE:
        session["age"] = int(user_input)
        session["state"] = USSDPersonalInfo.COMPLETE_GENDER
        return con("Enter your gender. M for Male; F for Female")
    
    if state == USSDPersonalInfo.COMPLETE_GENDER:
        session["gender"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_NATIONALITY
        return con("Enter your Nationality")
    
    if state == USSDPersonalInfo.COMPLETE_NATIONALITY:
        session["nationality"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_COUNTRY_OF_RESIDENCE
        return  con("Enter your country of Residence")
    
    if state == USSDPersonalInfo.COMPLETE_COUNTRY_OF_RESIDENCE:
        session["country_residence"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_CITY_OF_RESIDENCE
        return con("Enter your city of Residence")
    
    if state == USSDPersonalInfo.COMPLETE_CITY_OF_RESIDENCE:
        session["city_of_residence"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_ADDRESS
        return con("Enter your full address")
    
    if state == USSDPersonalInfo.COMPLETE_ADDRESS:
        session["address"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_NEXT_KIN
        return con("Enter the name of your next of kin: someone to contact in case of emergency")

    if state == USSDPersonalInfo.COMPLETE_NEXT_KIN:
        session["next_kin"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_NEXT_KIN_RELATIONSHIP
        return con("Enter next kin relationship. eg. Brother, Sister, Father")
    
    if state == USSDPersonalInfo.COMPLETE_NEXT_KIN_RELATIONSHIP:
        session["relationship"] = user_input.upper()
        session["state"] = USSDPersonalInfo.COMPLETE_NEXT_KIN_PHONE_NUMBER
        return con("Enter next of kin phone number. eg. 0789589895")
    
    if state == USSDPersonalInfo.COMPLETE_NEXT_KIN_PHONE_NUMBER:
        session["kin_phone_number"] = user_input
        session["state"] = USSDPersonalInfo.COMPLETE_PREFERRED_LANGUAGE
        return con("Enter your preferred language. eg. French, Swahili, Lingala, Kinkongo")
    
    if state == USSDPersonalInfo.COMPLETE_PREFERRED_LANGUAGE:
        session["preferred_language"] = user_input.upper()
        registration_details = {
            "age":session["age"],
            "gender":session["gender"],
            "nationality":session["nationality"],
            "country_of_residence":session["country_residence"],
            "city_of_residence":session["city_of_residence"],
            "address":session["address"],
            "next_of_kin":session["next_kin"],
            "next_of_kin_phone_number":session["kin_phone_number"],
            "patient_next_relationship":session["relationship"],
            "preferred_language":session["preferred_language"]
        }

        try:
            personal_info_data = patient_schema(**registration_details)
        except Exception as validation_error:
            return end("Registration Failed. Invalid Input")
        
        try:
            patient_id = session["patient_id"]
            personal_info = PatientPersonalInfo(**personal_info_data.model_dump(mode="json"),
                                                patient_id = patient_id,
                                                updated_at = datetime.utcnow())
            db.add(personal_info)
            db.commit()
            db.refresh(personal_info)
        except Exception as db_error:
            return end("Registration failed. Please try again later")

        return end(f"Personal Information save successfuly\nPatient Name: {existing_user.first_name} {existing_user.last_name}")

def view_personal_info(session, user_input, db:Session):
    """View Personal Info"""
    user_input = user_input.strip()
    state = session["state"]
    phone_number = session["phone"]

    existing_user = search_user(db=db, phone_number=phone_number, model=PatientRegistration)
    
    if not existing_user:
        return end("User not found! Register to MedCall to access this page")

    if state == USSDPersonalInfo.VERIFY_PIN:
        session["pin"] = user_input
        session["patient_id"] = existing_user.id
        if not bcrypt.checkpw(
            session["pin"].encode("utf-8"),
            existing_user.pin.encode("utf-8")
            ):
            return end("Incorrect PIN. Try again later")
        
        personal_data = search_patient_data(
            db=db,
            model=PatientPersonalInfo,
            patient_id=session["patient_id"]
        ).first()

        patient_data = dict_personal_info(model=personal_data)

        data = f"Age: {patient_data["age"]}\n" \
               f"Gender: {patient_data["gender"]}\n" \
               f"Nationality: {patient_data["nationality"]}\n" \
               f"Country of Residence: {patient_data["country_of_residence"]}\n" \
               f"City of Residence: {patient_data["city_of_residence"]}\n" \
               f"Address: {patient_data["address"]}\n" \
               f"Next of Kin: {patient_data["next_of_kin"]}\n" \
               f"Next of Kin Phone Number: {patient_data["next_of_kin_phone_number"]}\n" \
               f"Next of Kin Relationship: {patient_data["patient_next_relationship"]}\n" \
               f"Preferred Language: {patient_data["preferred_language"]}\n"
        return end(f"Patient data\n:{data}")
