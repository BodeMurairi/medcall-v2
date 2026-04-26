#!/usr/bin/env python3

from services.ussd.session import get_session, save_session

from services.ussd.state import (
    USSDState,
    PersonalInfoMenu,
    MedicalInfoMenu,
    USSDMedicalInfo,
    USSDPersonalInfo,
    ViewInfo,
    ViewPersonalInfo,
    ConsultationHistory,
)

from services.ussd.flows.menu_flow import main_menu, personal_info_submenu, medical_info_submenu
from services.ussd.flows.registration_flow import registration_flow
from services.ussd.flows.medical_info import save_medical_info, view_medical_info
from services.ussd.flows.complete_personal_infoflow import complete_personal_info_flow, view_personal_info
from services.ussd.flows.view_conversation import consultation_history_flow

from services.ussd.response import end

from sqlalchemy.orm import Session


def extract_input(text: str):
    if not text:
        return ""
    return text.split("*")[-1]


def ussd_engine(session_id, text, phone_number, db: Session):

    session = get_session(session_id)

    if not session:
        session = {
            "phone": phone_number,
            "state": USSDState.MAIN_MENU,
        }

    state = session["state"]
    user_input = extract_input(text)

    # ── Main Menu ────────────────────────────────────────────────────────────
    if state == USSDState.MAIN_MENU:
        if user_input == "":
            response = main_menu(session)

        elif user_input == "1":
            session["state"] = USSDState.REGISTER_FIRST_NAME
            response = "CON Enter your first name\n0. Back"

        elif user_input == "2":
            response = personal_info_submenu(session)

        elif user_input == "3":
            response = medical_info_submenu(session)

        elif user_input == "4":
            session["state"] = ConsultationHistory.VERIFY_PIN
            response = "CON Enter your PIN to view consultations\n0. Back"

        elif user_input == "0":
            response = end("Thank you for using MedCall. Goodbye!")

        else:
            response = end("Invalid option. Please redial.")

        save_session(session_id, session)
        return response

    # ── Personal Info Sub-Menu ───────────────────────────────────────────────
    if state == PersonalInfoMenu.MENU:
        if user_input == "0":
            response = main_menu(session)
        elif user_input == "1":
            session["state"] = USSDPersonalInfo.VERIFY_PIN
            response = "CON Enter your PIN to update personal info\n0. Back"
        elif user_input == "2":
            session["state"] = ViewPersonalInfo.VERIFY_PIN
            response = "CON Enter your PIN to view personal info\n0. Back"
        else:
            response = personal_info_submenu(session)

        save_session(session_id, session)
        return response

    # ── Medical Info Sub-Menu ────────────────────────────────────────────────
    if state == MedicalInfoMenu.MENU:
        if user_input == "0":
            response = main_menu(session)
        elif user_input == "1":
            session["state"] = USSDMedicalInfo.VERIFY_PIN
            response = "CON Enter your PIN to update medical info\n0. Back"
        elif user_input == "2":
            session["state"] = ViewInfo.VERIFY_PIN
            response = "CON Enter your PIN to view medical info\n0. Back"
        else:
            response = medical_info_submenu(session)

        save_session(session_id, session)
        return response

    # ── All other flows ──────────────────────────────────────────────────────
    if state.name.startswith("REGISTER"):
        response = registration_flow(session, user_input, db=db)

    elif isinstance(state, USSDPersonalInfo):
        response = complete_personal_info_flow(session, user_input, db=db)

    elif isinstance(state, USSDMedicalInfo):
        response = save_medical_info(session, user_input, db=db)

    elif isinstance(state, ViewInfo):
        response = view_medical_info(session, user_input, db=db)

    elif isinstance(state, ViewPersonalInfo):
        response = view_personal_info(session, user_input, db=db)

    elif isinstance(state, ConsultationHistory):
        response = consultation_history_flow(session, user_input, db=db)

    else:
        response = end("Something went wrong. Please redial.")

    save_session(session_id, session)
    return response
