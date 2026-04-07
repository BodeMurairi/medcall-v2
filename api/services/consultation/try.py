#!/usr/bin/env python3

import json
import asyncio
from langchain.messages import HumanMessage

from services.consultation.verify_consultation import check_user
from services.consultation.clean_consultation_data import parse_json
from services.consultation.save_consultation import save_consultation
from services.consultation.save_sms import save_consultation_sms

from external_integration.agents.agent.consultation import consultation_agent
from external_integration.agents.agent.analysis import analytic_agent
from external_integration.agents.utils.get_patient_ids import get_patient_id

from sqlalchemy.ext.asyncio import AsyncSession
from models.database_models import Consultation, ConsultationSMS, ConsultationAnalysis

agent = consultation_agent()
analysis_agent_class = analytic_agent


async def get_active_consultation(db: AsyncSession, patient_id: int):
    result = await db.execute(
        Consultation.__table__.select()
        .where(
            Consultation.patient_id == patient_id,
            Consultation.consultation_status == True
        )
        .order_by(Consultation.last_updated.desc())
    )
    return result.scalars().first()


async def trigger_analysis(db: AsyncSession, consultation: Consultation, patient_id: int, collected_data: dict):
    """
    Runs analytic_agent asynchronously and saves result to DB.
    """
    try:
        analysis_instance = analysis_agent_class(thread_id=str(consultation.id))

        # Fetch all conversation SMS asynchronously
        result = await db.execute(
            ConsultationSMS.__table__.select()
            .where(ConsultationSMS.consultation_id == consultation.id)
        )
        conversation = [{"type": row.message_type, "content": row.content} for row in result.scalars().all()]

        analysis_input = {
            "patient_id": patient_id,
            "consultation_id": str(consultation.id),
            "collected_data": collected_data,
            "consultation_summary": consultation.consultation_summary,
            "conversation": conversation
        }

        # Run the agent in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        analysis_response = await loop.run_in_executor(
            None,
            lambda: analysis_instance.invoke(
                {"messages": [HumanMessage(content=json.dumps(analysis_input))]},
                config={"configurable": {"thread_id": str(consultation.id)}}
            )
        )

        raw_analysis = analysis_response["messages"][-1].content
        analysis_json = parse_json(raw_content=raw_analysis)

        # Save analysis to DB asynchronously
        new_record = ConsultationAnalysis(
            consultation_id=consultation.id,
            detected_symptoms=json.dumps(analysis_json.get("detected_symptoms", [])),
            possible_conditions=json.dumps(analysis_json.get("possible_conditions", [])),
            exams=json.dumps(analysis_json.get("exams", {})),
            risk_level=analysis_json.get("risk_level", "low"),
            mark_emergency=analysis_json.get("mark_emergency", False),
            reasoning=analysis_json.get("reasoning", "")
        )
        db.add(new_record)
        await db.commit()
        print(f"[INFO] Analysis saved for consultation {consultation.id}")

    except Exception as e:
        print(f"[ERROR] Analysis failed for consultation {consultation.id}: {e}")


async def handle_consultation(db: AsyncSession, phone_number: str, user_input: str, thread_id: str):
    check_phone = check_user(phone_number=phone_number)

    if check_phone["status"] == "complete" or not check_phone["register"]:
        return {
            "status": "complete",
            "message": check_phone["current_message"],
            "consultation_id": None
        }

    patient_id = get_patient_id(phone_number=phone_number)
    active_consultation = await get_active_consultation(db, patient_id)
    current_thread_id = active_consultation.thread_id if active_consultation else thread_id

    # Run consultation agent in executor to avoid blocking
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: agent.invoke(
            {"messages": [HumanMessage(content=f"user question: {user_input}\nuser phone number: {phone_number}")]},
            config={"configurable": {"thread_id": current_thread_id}}
        )
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

    # Save SMS
    save_consultation_sms(db, active_consultation.id, "user", user_input)
    ai_content = consultation_data.get("current_message")
    if ai_content:
        tool_call = consultation_data.get("tool_call")
        sms_metadata = json.dumps({"tool_call": tool_call}) if tool_call and tool_call.get("name") else None
        save_consultation_sms(db, active_consultation.id, "ai", ai_content, sms_metadata)

    # Update consultation
    active_consultation.risk_level = risk_level
    active_consultation.consultation_summary = consultation_summary
    active_consultation.consultation_status = is_active
    await db.commit()

    # Trigger analysis asynchronously if consultation is complete
    if not is_active:
        asyncio.create_task(trigger_analysis(db, active_consultation, patient_id, collected_data))

    return {
        "status": consultation_data.get("status"),
        "message": ai_content,
        "consultation_id": active_consultation.id,
        "thread_id": current_thread_id
    }
