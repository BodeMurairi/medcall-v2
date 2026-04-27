#!/usr/bin/env python3

import bcrypt
import json
from sqlalchemy.orm import Session

from models.database_models import PatientRegistration, Consultation
from services.ussd.response import con, end
from services.ussd.state import ConsultationHistory, USSDState
from services.sms.send_sms import send_sms

_WEB_APP_URL = "https://medcall-hazel.vercel.app"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_patient(db, phone_number):
    return db.query(PatientRegistration).where(
        PatientRegistration.phone_number == phone_number
    ).first()


def _get_consultations(db, patient_id):
    return (
        db.query(Consultation)
        .where(Consultation.patient_id == patient_id)
        .order_by(Consultation.start_time.desc())
        .limit(5)
        .all()
    )


def _get_consultation_by_id(db, consultation_id):
    return db.query(Consultation).where(Consultation.id == consultation_id).first()


def _truncate(text, max_len):
    if not text:
        return "N/A"
    text = str(text)
    return text[:max_len] + "..." if len(text) > max_len else text


def _parse_json_field(value):
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else [str(parsed)]
    except (json.JSONDecodeError, TypeError):
        return [str(value)]


# ── Screen builders ───────────────────────────────────────────────────────────

def _show_list(session, db):
    consultations = _get_consultations(db, session["patient_id"])
    if not consultations:
        send_sms(
            session["phone"],
            f"Hi! You have no consultations on MedCall yet. "
            f"Visit {_WEB_APP_URL} to chat with Doctor Mshauri "
            f"and start your first consultation.",
        )
        return end(
            "No consultations found.\n"
            "Send SMS to MedCall or use the web app\n"
            "to start your first consultation."
        )

    lines = ["Your Consultations:"]
    for i, c in enumerate(consultations, 1):
        date = c.start_time.strftime("%d/%m/%Y") if c.start_time else "Unknown"
        summary = _truncate(c.consultation_summary or "In progress", 30)
        lines.append(f"{i}. {date} - {summary}")
    lines.append("0. Main Menu")

    session["state"] = ConsultationHistory.LIST
    return con("\n".join(lines))


def _show_detail_menu(session, consultation):
    date = consultation.start_time.strftime("%d/%m/%Y") if consultation.start_time else "Unknown"
    status = "Complete" if not consultation.consultation_status else "Active"
    session["state"] = ConsultationHistory.DETAIL_MENU
    return con(
        f"Consultation {date} ({status})\n"
        "1. Summary\n"
        "2. Analysis\n"
        "3. Doctor Decision\n"
        "0. Back to List"
    )


def _show_summary(session, consultation):
    summary = _truncate(consultation.consultation_summary or "No summary yet.", 160)
    session["state"] = ConsultationHistory.SUMMARY
    return con(f"Summary:\n{summary}\n\n0. Back")


def _show_analysis(session, consultation):
    session["state"] = ConsultationHistory.ANALYSIS

    if not consultation.analysis:
        return con("Analysis not ready yet.\nCheck back soon.\n\n0. Back")

    a = consultation.analysis
    symptoms   = _parse_json_field(a.detected_symptoms)
    conditions = _parse_json_field(a.possible_conditions)

    symptoms_str   = _truncate(", ".join(symptoms), 55)
    conditions_str = _truncate(", ".join(conditions), 55)
    emergency_str  = "YES - Seek urgent care!" if a.mark_emergency else "No"

    return con(
        f"Analysis:\n"
        f"Risk: {a.risk_level}\n"
        f"Emergency: {emergency_str}\n"
        f"Symptoms: {symptoms_str}\n"
        f"Conditions: {conditions_str}\n"
        f"0. Back"
    )


def _show_decision(session, consultation):
    session["state"] = ConsultationHistory.DECISION

    if not consultation.decision:
        return con("Decision not ready yet.\nCheck back soon.\n\n0. Back")

    d = consultation.decision
    action  = (d.action or "N/A").replace("_", " ").title()
    urgency = d.urgency or "N/A"
    message = _truncate(d.message, 100)

    return con(
        f"Doctor Decision:\n"
        f"Action: {action}\n"
        f"Urgency: {urgency}\n"
        f"{message}\n"
        f"0. Back"
    )


# ── Main flow dispatcher ──────────────────────────────────────────────────────

def consultation_history_flow(session, user_input, db: Session):

    user_input = user_input.strip()
    state = session["state"]
    phone_number = session["phone"]

    patient = _get_patient(db, phone_number)
    if not patient:
        return end("Not registered. Redial and choose Register.")

    # ── PIN verification ──────────────────────────────────────────────────────
    if state == ConsultationHistory.VERIFY_PIN:
        if user_input == "0":
            from services.ussd.flows.menu_flow import main_menu
            return main_menu(session)

        if not bcrypt.checkpw(user_input.encode("utf-8"), patient.pin.encode("utf-8")):
            return end("Incorrect PIN. Please redial.")

        session["patient_id"] = patient.id
        return _show_list(session, db)

    # ── Consultation list ─────────────────────────────────────────────────────
    if state == ConsultationHistory.LIST:
        if user_input == "0":
            from services.ussd.flows.menu_flow import main_menu
            return main_menu(session)

        consultations = _get_consultations(db, session["patient_id"])
        try:
            idx = int(user_input) - 1
            if idx < 0 or idx >= len(consultations):
                raise ValueError
        except (ValueError, TypeError):
            return _show_list(session, db)

        selected = consultations[idx]
        session["selected_consultation_id"] = selected.id
        return _show_detail_menu(session, selected)

    # ── Detail menu ───────────────────────────────────────────────────────────
    if state == ConsultationHistory.DETAIL_MENU:
        if user_input == "0":
            return _show_list(session, db)

        consultation = _get_consultation_by_id(db, session.get("selected_consultation_id"))
        if not consultation:
            return _show_list(session, db)

        if user_input == "1":
            return _show_summary(session, consultation)
        elif user_input == "2":
            return _show_analysis(session, consultation)
        elif user_input == "3":
            return _show_decision(session, consultation)
        else:
            return _show_detail_menu(session, consultation)

    # ── Detail views — any input goes back to detail menu ─────────────────────
    if state in (
        ConsultationHistory.SUMMARY,
        ConsultationHistory.ANALYSIS,
        ConsultationHistory.DECISION,
    ):
        consultation = _get_consultation_by_id(db, session.get("selected_consultation_id"))
        if not consultation:
            return _show_list(session, db)
        return _show_detail_menu(session, consultation)

    return end("Unexpected state. Please redial.")
