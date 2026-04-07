#!/usr/bin/env python3

import bcrypt
from datetime import datetime
from sqlalchemy.orm import Session
from models.database_models import PatientRegistration
from schemas.users import PatientRegistration as registration_schema
from database.session import get_db
from services.ussd.response import con, end
from services.ussd.state import USSDState

def registration_flow(session, user_input, db: Session):

    user_input = user_input.strip()
    state = session["state"]
    phone_number = session["phone"]

    if state == USSDState.REGISTER_FIRST_NAME:
        session["first_name"] = user_input.upper()
        session["state"] = USSDState.REGISTER_LAST_NAME
        return con("Enter your last name")

    if state == USSDState.REGISTER_LAST_NAME:
        session["last_name"] = user_input.upper()
        session["state"] = USSDState.REGISTER_EMAIL
        return con("Enter your email (or 'none')")

    if state == USSDState.REGISTER_EMAIL:
        session["email"] = user_input.upper() if user_input else None
        session["state"] = USSDState.REGISTER_PIN
        return con("Enter your PIN")

    if state == USSDState.REGISTER_PIN:
        session["pin"] = user_input
        session["state"] = USSDState.REGISTER_CONFIRM_PIN
        return con("Confirm your PIN")

    if state == USSDState.REGISTER_CONFIRM_PIN:
        if user_input != session["pin"]:
            return end("PIN mismatch. Registration failed.")

        # Hash the PIN
        hashed_pin = bcrypt.hashpw(session["pin"].encode(), bcrypt.gensalt())

        # Gather all details
        registration_data = {
            "first_name": session["first_name"].upper(),
            "last_name": session["last_name"].upper(),
            "email_address": session["email"],
            "phone_number": phone_number,
            "pin": hashed_pin.decode()
        }
        
        try:
            patient_data = registration_schema(**registration_data)
        except Exception as validation_error:
            print(f"\nfailed to register:\n{validation_error}")
            end("Registration failed. Invalid input")
        try:
            new_patient = PatientRegistration(**patient_data.model_dump(mode="json"), updated_at=datetime.utcnow())
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)
        except Exception as db_error:
            print(f"\nValue error:\n {db_error}")
            print("DEBUG: Registration failed:", db_error)
            end("Registration failed. Try later")

        return end(
            "Registration successful. Welcome to MedCall\nRegistration Details:\n"
            f"First name: {registration_data['first_name']}\n"
            f"Last name: {registration_data['last_name']}\n"
            f"Email address: {registration_data['email_address']}\n"
            f"Phone Number: {registration_data['phone_number']}"
        )
