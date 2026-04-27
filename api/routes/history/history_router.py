#!/usr/bin/env python3

import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Any

from database.session import get_db
from models.database_models import (
    PatientRegistration, Consultation, ConsultationSMS,
    ConsultationAnalysis, ConsultationDecision
)
from utils.jwt_utils import get_current_patient

router = APIRouter(prefix="/history", tags=["History"])


class SMSItem(BaseModel):
    message_type: str
    content: str
    timestamp: Optional[str]

class AnalysisItem(BaseModel):
    detected_symptoms: Any
    red_flags: Optional[Any]
    key_negatives: Optional[Any]
    possible_conditions: Any
    exams: Any
    risk_level: str
    risk_justification: Optional[str]
    mark_emergency: bool
    reasoning: Optional[str]

class DecisionItem(BaseModel):
    message: str
    urgency: str
    action: str
    referral_type: Optional[str]
    referral_explanation: Optional[str]
    referral_options: Optional[Any]

class ConsultationHistoryItem(BaseModel):
    id: int
    consultation_id: str
    start_time: Optional[str]
    last_updated: Optional[str]
    risk_level: Any
    status: str
    summary: Optional[str]
    messages: List[SMSItem]
    analysis: Optional[AnalysisItem]
    decision: Optional[DecisionItem]


def _safe_json(value):
    if value is None:
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


@router.get("", response_model=List[ConsultationHistoryItem])
def get_history(
    db: Session = Depends(get_db),
    patient: PatientRegistration = Depends(get_current_patient),
):
    """Return all consultations (latest first) for the authenticated patient."""
    consultations = (
        db.query(Consultation)
        .filter(Consultation.patient_id == patient.id)
        .order_by(Consultation.start_time.desc())
        .all()
    )

    result = []
    for c in consultations:
        messages = [
            SMSItem(
                message_type=sms.message_type,
                content=sms.content,
                timestamp=sms.timestamp.isoformat() if sms.timestamp else None
            )
            for sms in c.consultation_sms
        ]

        analysis = None
        if c.analysis:
            a = c.analysis
            analysis = AnalysisItem(
                detected_symptoms=_safe_json(a.detected_symptoms),
                red_flags=_safe_json(a.red_flags),
                key_negatives=_safe_json(a.key_negatives),
                possible_conditions=_safe_json(a.possible_conditions),
                exams=_safe_json(a.exams),
                risk_level=a.risk_level,
                risk_justification=a.risk_justification,
                mark_emergency=a.mark_emergency,
                reasoning=a.reasoning
            )

        decision = None
        if c.decision:
            d = c.decision
            decision = DecisionItem(
                message=d.message,
                urgency=d.urgency,
                action=d.action,
                referral_type=d.referral_type,
                referral_explanation=d.referral_explanation,
                referral_options=_safe_json(d.referral_options),
            )

        result.append(ConsultationHistoryItem(
            id=c.id,
            consultation_id=c.consultation_id,
            start_time=c.start_time.isoformat() if c.start_time else None,
            last_updated=c.last_updated.isoformat() if c.last_updated else None,
            risk_level=c.risk_level,
            status="active" if c.consultation_status else "complete",
            summary=c.consultation_summary,
            messages=messages,
            analysis=analysis,
            decision=decision
        ))

    return result
