#!/usr/bin/env python3

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from schemas.consultation_schema import (
    ConsultationRequest,
    ConsultationResponse
)

from controllers.consultation.consultation import consult_controller
from database.session import get_db
from models.database_models import Consultation, ConsultationSMS, PatientRegistration
from utils.jwt_utils import get_current_patient

router = APIRouter(
    prefix="/consultation",
    tags=["ConsultationManagement"]
)


class ActiveMessageItem(BaseModel):
    role: str
    content: str
    timestamp: Optional[str]

class ActiveConsultationResponse(BaseModel):
    found: bool
    thread_id: Optional[str] = None
    messages: Optional[List[ActiveMessageItem]] = None


@router.post("", response_model=ConsultationResponse)
def consult(request: ConsultationRequest, db: Session = Depends(get_db)):
    return consult_controller(db, request)


@router.get("/active", response_model=ActiveConsultationResponse)
def get_active_consultation(
    db: Session = Depends(get_db),
    patient: PatientRegistration = Depends(get_current_patient),
):
    """Return the latest unfinished consultation for the authenticated patient, if any."""
    active = (
        db.query(Consultation)
        .filter(
            Consultation.patient_id == patient.id,
            Consultation.consultation_status == True,
        )
        .order_by(Consultation.start_time.desc())
        .first()
    )

    if not active:
        return ActiveConsultationResponse(found=False)

    messages = [
        ActiveMessageItem(
            role=sms.message_type,
            content=sms.content,
            timestamp=sms.timestamp.isoformat() if sms.timestamp else None,
        )
        for sms in active.consultation_sms
    ]

    return ActiveConsultationResponse(
        found=True,
        thread_id=active.thread_id,
        messages=messages,
    )
