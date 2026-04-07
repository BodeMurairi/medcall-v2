#!/usr/bin/env python3

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Any

from database.session import get_db
from models.database_models import PatientRegistration, Consultation
from utils.jwt_utils import get_current_patient

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationItem(BaseModel):
    id: int
    consultation_id: str
    start_time: Optional[str]
    last_updated: Optional[str]
    has_analysis: bool
    has_decision: bool
    urgency: Optional[str]
    action: Optional[str]
    risk_level: Any


@router.get("", response_model=List[NotificationItem])
def get_notifications(
    db: Session = Depends(get_db),
    patient: PatientRegistration = Depends(get_current_patient),
):
    """
    Return completed consultations that have analysis or decision results ready.
    The frontend uses this to drive the notification bell badge.
    """
    consultations = (
        db.query(Consultation)
        .filter(
            Consultation.patient_id == patient.id,
            Consultation.consultation_status == False,   # only completed ones
        )
        .order_by(Consultation.last_updated.desc())
        .limit(30)
        .all()
    )

    result = []
    for c in consultations:
        has_analysis = c.analysis is not None
        has_decision = c.decision is not None
        # Only surface a notification when at least the analysis is done
        if has_analysis or has_decision:
            result.append(NotificationItem(
                id=c.id,
                consultation_id=c.consultation_id,
                start_time=c.start_time.isoformat() if c.start_time else None,
                last_updated=c.last_updated.isoformat() if c.last_updated else None,
                has_analysis=has_analysis,
                has_decision=has_decision,
                urgency=c.decision.urgency if c.decision else None,
                action=c.decision.action if c.decision else None,
                risk_level=c.risk_level,
            ))

    return result
