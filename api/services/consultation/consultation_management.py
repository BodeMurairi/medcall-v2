#!/usr/bin/env python3

import json
import time
import threading
from threading import Thread
from langchain_core.messages import HumanMessage

from services.consultation.verify_consultation import check_user
from services.consultation.clean_consultation_data import parse_json, sanitize_nan
from services.consultation.save_consultation import save_consultation
from services.consultation.save_sms import save_consultation_sms

from external_integration.agents.agent.consultation import consultation_agent
from external_integration.agents.agent.analysis import analytic_agent
from external_integration.agents.utils.get_patient_ids import get_patient_id

from sqlalchemy.orm import Session
from models.database_models import Consultation, ConsultationSMS, ConsultationAnalysis, PatientRegistration
from database.create_session import SessionLocal

agent = consultation_agent()
analysis_agent_class = analytic_agent

# Limit concurrent analysis threads so they don't all fire simultaneously
# and exhaust every API key's quota at once
_analysis_semaphore = threading.Semaphore(2)


def get_active_consultation(db: Session, patient_id: int):
    return (
        db.query(Consultation)
        .filter(
            Consultation.patient_id == patient_id,
            Consultation.consultation_status == True
        )
        .order_by(Consultation.last_updated.desc())
        .first()
    )


def _retry_pending_analysis(patient_id: int):
    """
    Background task: opens its own session, finds every completed consultation
    that has no analysis record, and fires a separate analysis thread for each.
    Never called on the request thread — always run via Thread(...).start().
    """
    db = SessionLocal()
    try:
        pending = (
            db.query(Consultation)
            .outerjoin(ConsultationAnalysis, ConsultationAnalysis.consultation_id == Consultation.id)
            .filter(
                Consultation.patient_id == patient_id,
                Consultation.consultation_status == False,
                ConsultationAnalysis.id == None
            )
            .all()
        )
        for c in pending:
            print(f"[INFO] Retrying missed analysis for consultation {c.id}")
            Thread(target=trigger_analysis, args=(c.id, patient_id, {}), daemon=True).start()
    except Exception as e:
        print(f"[ERROR] Pending analysis check failed for patient {patient_id}: {e}")
    finally:
        db.close()


def trigger_analysis(consultation_id: int, patient_int_id: int, collected_data: dict):
    """
    Runs the analytic_agent in a separate thread with its own db session.
    Acquires a semaphore so at most 2 analyses run concurrently, preventing
    simultaneous quota exhaustion across all API keys.
    Args:
        consultation_id: integer PK of the consultation
        patient_int_id: integer PK of the patient (patients.id)
        collected_data: symptoms/severity data from the consultation
    """
    with _analysis_semaphore:
        _run_analysis(consultation_id, patient_int_id, collected_data)


def _run_analysis(consultation_id: int, patient_int_id: int, collected_data: dict):
    """Inner function that performs the actual analysis with retry on rate-limit errors."""
    max_retries = 3
    retry_wait = 45  # seconds to wait on RESOURCE_EXHAUSTED before retrying

    for attempt in range(max_retries):
        db = SessionLocal()
        try:
            consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
            if not consultation:
                print(f"[ERROR] Consultation {consultation_id} not found in analysis thread")
                return

            # Get the string patient_id (e.g. "Patient-abc123") for the tool
            patient = db.query(PatientRegistration).filter(PatientRegistration.id == patient_int_id).first()
            string_patient_id = patient.patient_id if patient else str(patient_int_id)

            # analytic_agent returns (agent, thread_id) — unpack correctly
            agent_instance, _ = analysis_agent_class(thread_id=str(consultation_id))

            conversation = [
                {"type": sms.message_type, "content": sms.content}
                for sms in db.query(ConsultationSMS)
                            .filter(ConsultationSMS.consultation_id == consultation_id)
                            .all()
            ]

            analysis_input = {
                "patient_id": string_patient_id,
                "consultation_id": str(consultation_id),
                "collected_data": collected_data,
                "consultation_summary": consultation.consultation_summary,
                "conversation": conversation
            }

            analysis_response = agent_instance.invoke(
                {"messages": [HumanMessage(content=json.dumps(sanitize_nan(analysis_input)))]},
                config={"configurable": {"thread_id": str(consultation_id)}}
            )

            raw_analysis = analysis_response["messages"][-1].content
            analysis_json = parse_json(raw_content=raw_analysis)

            if isinstance(analysis_json, dict) and analysis_json:
                analysis_record = ConsultationAnalysis(
                    consultation_id=consultation_id,
                    detected_symptoms=json.dumps(analysis_json.get("detected_symptoms", [])),
                    possible_conditions=json.dumps(analysis_json.get("possible_conditions", [])),
                    exams=json.dumps(analysis_json.get("exams", {})),
                    risk_level=analysis_json.get("risk_level", "low"),
                    mark_emergency=analysis_json.get("mark_emergency", False),
                    reasoning=analysis_json.get("reasoning", "")
                )
                db.add(analysis_record)
                db.commit()
                print(f"[INFO] Analysis saved for consultation {consultation_id}")
            else:
                print(f"[WARN] Analysis returned empty or invalid JSON for consultation {consultation_id}")
            return  # success — exit retry loop

        except Exception as e:
            error_str = str(e)
            if "RESOURCE_EXHAUSTED" in error_str and attempt < max_retries - 1:
                wait = retry_wait * (attempt + 1)
                print(f"[WARN] Rate limited on consultation {consultation_id} (attempt {attempt + 1}/{max_retries}), retrying in {wait}s...")
                db.close()
                time.sleep(wait)
            else:
                print(f"[ERROR] Analysis failed for consultation {consultation_id}: {e}")
                return
        finally:
            try:
                db.close()
            except Exception:
                pass


def handle_consultation(db: Session, phone_number: str, user_input: str, thread_id: str):
    check_phone = check_user(phone_number=phone_number)

    if check_phone["status"] == "complete" or not check_phone["register"]:
        return {
            "status": "complete",
            "message": check_phone["current_message"],
            "consultation_id": None
        }

    patient_id = get_patient_id(phone_number=phone_number)
    active_consultation = get_active_consultation(db=db, patient_id=patient_id)

    # If no active consultation, asynchronously check for completed consultations
    # whose analysis was never saved and retry them — no blocking on the request thread
    if not active_consultation:
        Thread(target=_retry_pending_analysis, args=(patient_id,), daemon=True).start()

    current_thread_id = active_consultation.thread_id if active_consultation else thread_id

    # Send message to consultation agent
    response = agent.invoke(
        {"messages": [HumanMessage(content=f"user question: {user_input}\nuser phone number: {phone_number}")]},
        config={"configurable": {"thread_id": current_thread_id}},
    )

    raw_content = response["messages"][-1].content
    consultation_result = parse_json(raw_content=raw_content)
    consultation_data = consultation_result[-1] if isinstance(consultation_result, list) else consultation_result

    if not isinstance(consultation_data, dict):
        return {"status": "error", "message": "Invalid AI response format", "consultation_id": None}

    collected_data = consultation_data.get("collected_data", {})
    severity = collected_data.get("severity", {})
    risk_level = ",".join(severity.values()) if severity else None
    consultation_summary = consultation_data.get("consultation_summary") or consultation_data.get("summary") or ""
    is_active = consultation_data.get("status", "in_progress") != "complete"

    if not active_consultation:
        active_consultation = save_consultation(
            db=db,
            patient_id=patient_id,
            risk_level=risk_level,
            consultation_summary=consultation_summary,
            consultation_status=is_active,
            thread_id=current_thread_id
        )
        if not active_consultation:
            return {"status": "error", "message": "Failed to save consultation", "consultation_id": None}

    # Save SMS messages
    save_consultation_sms(db, active_consultation.id, "user", user_input, None)
    ai_content = consultation_data.get("current_message")
    if ai_content:
        tool_call = consultation_data.get("tool_call")
        sms_metadata = json.dumps({"tool_call": tool_call}) if tool_call and tool_call.get("name") else None
        save_consultation_sms(db, active_consultation.id, "ai", ai_content, sms_metadata)

    # Update consultation record
    active_consultation.risk_level = risk_level
    active_consultation.consultation_summary = consultation_summary
    active_consultation.consultation_status = is_active
    db.commit()

    # Trigger background analysis when consultation is complete
    if not is_active:
        Thread(
            target=trigger_analysis,
            args=(active_consultation.id, patient_id, collected_data),
            daemon=True
        ).start()

    return {
        "status": consultation_data.get("status"),
        "message": ai_content,
        "consultation_id": active_consultation.id,
        "thread_id": current_thread_id
    }
