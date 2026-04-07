#!/usr/bin/env python3

import uuid
from services.consultation.consultation import handle_consultation

def consult_controller(db, request):
    """this is the consultation controller"""
    thread_id = str(uuid.uuid4()).split("-")[2]

    result = handle_consultation(
        db=db,
        phone_number=request.phone_number,
        user_input=request.message,
        thread_id=thread_id
    )

    print(f"[INFO] Consultation handled: {result.get('consultation_id')}")

    return result
