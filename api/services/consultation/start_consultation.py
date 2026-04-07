#!/usr/bin/env python3

import json
from langchain.messages import HumanMessage
from sqlalchemy.orm import Session

from services.consultation.verify_consultation import check_user
from services.consultation.clean_consultation_data import parse_json
from services.consultation.save_consultation import save_consultation
from services.consultation.save_sms import save_consultation_sms
from database.session import get_db

from external_integration.agents.agent.consultation import consultation_agent
from external_integration.agents.utils.get_patient_ids import get_patient_id

print("=== MedCall Consultation Agent ===")
print("Type 'exit' at any time to end.\n")

# Get patient info
thread_id = input("Enter User ID (or phone number): ").strip()
phone_number = input("Enter your phone number: ").strip()

agent = consultation_agent()

# ONE DB SESSION FOR EVERYTHING
db: Session = next(get_db())

# Track consultation for this session
new_consultation = None

while True:
    user_input = input("User: ").strip()

    if user_input.lower() == "exit":
        print("\nExiting consultation...")
        break

    # Verify user registration
    check_phone = check_user(phone_number=phone_number)
    if check_phone["status"] == "complete" or not check_phone["register"]:
        print(check_phone["current_message"])
        break

    # Send user message to AI agent
    response = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=f"user question: {user_input}\nuser phone number: {phone_number}"
                )
            ]
        },
        config={"configurable": {"thread_id": thread_id}},
    )

    # Parse AI response
    raw_content = response["messages"][-1].content
    consultation_result = parse_json(raw_content=raw_content)

    consultation_data = (
        consultation_result[-1]
        if isinstance(consultation_result, list)
        else consultation_result
    )

    if not isinstance(consultation_data, dict):
        print("Invalid AI response format")
        continue

    # Extract structured data
    collected_data = consultation_data.get("collected_data", {})

    severity = collected_data.get("severity", {})
    risk_level = ",".join(severity.values()) if severity else None

    consultation_summary = (
        consultation_data.get("consultation_summary")
        or consultation_data.get("summary")
        or ""
    )

    # Status
    is_active = consultation_data.get("status", "in_progress") != "complete"

    patient_id = get_patient_id(phone_number=phone_number)

    # Create consultation ONCE
    if not new_consultation:
        new_consultation = save_consultation(
            db=db,
            patient_id=patient_id,
            risk_level=risk_level,
            consultation_summary=consultation_summary,
            consultation_status=is_active,
        )

        if not new_consultation:
            print("Failed to save consultation")
            break

    # Save USER message
    save_consultation_sms(
        db=db,
        consultation_id=new_consultation.id,
        message_type="user",
        content=user_input,
        sms_metadata=None
    )

    # Save AI message
    ai_content = consultation_data.get("current_message")

    if ai_content:
        tool_call = consultation_data.get("tool_call")

        sms_metadata = None
        if tool_call and tool_call.get("name"):
            sms_metadata = json.dumps({"tool_call": tool_call})

        save_consultation_sms(
            db=db,
            consultation_id=new_consultation.id,
            message_type="ai",
            content=ai_content,
            sms_metadata=sms_metadata,
        )

    new_consultation.risk_level = risk_level
    new_consultation.consultation_summary = consultation_summary
    new_consultation.consultation_status = is_active

    db.commit()

    # Output
    print(ai_content)
