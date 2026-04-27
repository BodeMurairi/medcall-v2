#!/usr/bin/env python3

import bcrypt
from datetime import datetime
from sqlalchemy.orm import Session
from models.database_models import PatientRegistration
from schemas.users import PatientRegistration as registration_schema
from services.ussd.response import con, end
from services.ussd.state import USSDState


def registration_flow(session, user_input, db: Session):

    user_input = user_input.strip()
    state = session["state"]
    phone_number = session["phone"]

    # 0 at any step cancels registration and returns to main menu
    if user_input == "0":
        from services.ussd.flows.menu_flow import main_menu
        # clear any partial registration data
        for key in ["first_name", "last_name", "email", "pin"]:
            session.pop(key, None)
        return main_menu(session)

    if state == USSDState.REGISTER_FIRST_NAME:
        session["first_name"] = user_input.upper()
        session["state"] = USSDState.REGISTER_LAST_NAME
        return con("Enter your last name\n0. Back")

    if state == USSDState.REGISTER_LAST_NAME:
        session["last_name"] = user_input.upper()
        session["state"] = USSDState.REGISTER_EMAIL
        return con("Enter your email (or type 'none')\n0. Back")

    if state == USSDState.REGISTER_EMAIL:
        session["email"] = user_input if user_input.lower() != "none" else None
        session["state"] = USSDState.REGISTER_PIN
        return con("Create a PIN\n0. Back")

    if state == USSDState.REGISTER_PIN:
        session["pin"] = user_input
        session["state"] = USSDState.REGISTER_CONFIRM_PIN
        return con("Confirm your PIN\n0. Back")

    if state == USSDState.REGISTER_CONFIRM_PIN:
        if user_input != session["pin"]:
            session["state"] = USSDState.REGISTER_PIN
            return con("PIN mismatch. Enter your PIN again\n0. Back")

        hashed_pin = bcrypt.hashpw(session["pin"].encode(), bcrypt.gensalt())

        registration_data = {
            "first_name": session["first_name"],
            "last_name": session["last_name"],
            "email_address": session.get("email"),
            "phone_number": phone_number,
            "pin": hashed_pin.decode(),
        }

        try:
            patient_data = registration_schema(**registration_data)
        except Exception:
            return end("Registration failed. Invalid input. Please redial.")

        existing = db.query(PatientRegistration).where(
            PatientRegistration.phone_number == phone_number
        ).first()
        if existing:
            return end(
                "This number is already registered.\n"
                "Redial and choose Personal or Medical Information."
            )

        try:
            new_patient = PatientRegistration(
                **patient_data.model_dump(mode="json"),
                updated_at=datetime.utcnow(),
            )
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)
        except Exception as e:
            print(f"Registration DB error: {e}")
            return end("Registration failed. Please try again later.")

        return end(
            f"Welcome to MedCall, {registration_data['first_name']}!\n"
            "Registration successful.\n"
            "Redial to complete your profile."
        )
