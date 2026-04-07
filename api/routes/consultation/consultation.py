#!/usr/bin/env python3

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas.consultation_schema import (
    ConsultationRequest,
    ConsultationResponse
)

from controllers.consultation.consultation import consult_controller
from database.session import get_db

router = APIRouter(
    prefix="/consultation",
    tags=["ConsultationManagement"]
    )

@router.post("", response_model=ConsultationResponse)
def consult(request: ConsultationRequest, db: Session = Depends(get_db)):
    return consult_controller(db, request)
