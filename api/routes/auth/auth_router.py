#!/usr/bin/env python3

import bcrypt
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

from database.session import get_db
from models.database_models import (
    PatientRegistration, PatientPersonalInfo, PatientMedicalInfo
)
from schemas.users import (
    PatientRegistration as RegistrationSchema,
    PatientPersonalInfo as PersonalInfoSchema,
    PatientMedicalInformation as MedicalInfoSchema,
)
from external_integration.agents.utils.normalize_phone import normalize_phone_number
from utils.jwt_utils import create_access_token, get_current_patient

router = APIRouter(prefix="/auth", tags=["Auth"])


# Schemas

class LoginRequest(BaseModel):
    phone_number: str
    pin: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    patient_id: str
    first_name: str
    last_name: str
    phone_number: str
    has_personal_info: bool
    has_medical_info: bool

class RegisterRequest(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone_number: str
    email_address: Optional[EmailStr] = None
    pin: str = Field(..., min_length=6)
    confirm_pin: str = Field(..., min_length=6)

class PersonalInfoRequest(BaseModel):
    age: int = Field(..., gt=0, lt=150)
    gender: str = Field(...)          # M | F | Other
    nationality: str = Field(..., min_length=1)
    country_of_residence: str = Field(..., min_length=1)
    city_of_residence: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    next_of_kin: Optional[str] = None
    next_of_kin_phone_number: Optional[str] = None
    patient_next_relationship: Optional[str] = None
    preferred_language: str = Field(..., min_length=1)

class MedicalInfoRequest(BaseModel):
    blood_type: str = Field(...)     # A+, A-, B+, B-, AB+, AB-, O+, O-
    allergies: Optional[str] = None
    chronic_illness: Optional[str] = None
    recent_vaccination: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_pin: str = Field(..., min_length=4)
    new_pin: str = Field(..., min_length=6)
    confirm_new_pin: str = Field(..., min_length=6)

class MessageResponse(BaseModel):
    message: str


# Helpers

def _hash_pin(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def _check_pin(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def _build_token_response(patient: PatientRegistration, db: Session) -> TokenResponse:
    token = create_access_token(patient.patient_id, patient.phone_number)
    has_personal = db.query(PatientPersonalInfo).filter(
        PatientPersonalInfo.patient_id == patient.id
    ).first() is not None
    has_medical = db.query(PatientMedicalInfo).filter(
        PatientMedicalInfo.patient_id == patient.id
    ).first() is not None
    return TokenResponse(
        access_token=token,
        patient_id=patient.patient_id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        phone_number=patient.phone_number,
        has_personal_info=has_personal,
        has_medical_info=has_medical,
    )


# Endpoints

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with phone number + PIN and return a JWT token."""
    try:
        normalized = normalize_phone_number(request.phone_number)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid phone number format.")

    patient = db.query(PatientRegistration).filter(
        PatientRegistration.phone_number == normalized
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Phone number not registered. Please create an account first."
        )

    if not _check_pin(request.pin, patient.pin):
        raise HTTPException(status_code=401, detail="Incorrect PIN.")

    return _build_token_response(patient, db)


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new patient account (step 1 of 3)."""
    if request.pin != request.confirm_pin:
        raise HTTPException(status_code=400, detail="PINs do not match.")

    try:
        normalized = normalize_phone_number(request.phone_number)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid phone number format.")

    existing = db.query(PatientRegistration).filter(
        PatientRegistration.phone_number == normalized
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Phone number already registered.")

    data = RegistrationSchema(
        first_name=request.first_name.upper(),
        last_name=request.last_name.upper(),
        phone_number=normalized,
        email_address=request.email_address,
        pin=_hash_pin(request.pin),
    )
    patient = PatientRegistration(**data.model_dump(mode="json"), updated_at=datetime.utcnow())
    db.add(patient)
    db.commit()
    db.refresh(patient)

    return _build_token_response(patient, db)


@router.post("/register/personal", response_model=MessageResponse)
def save_personal_info(
    request: PersonalInfoRequest,
    db: Session = Depends(get_db),
    patient: PatientRegistration = Depends(get_current_patient),
):
    """Save / update personal information (step 2 of 3)."""
    valid_genders = {"M", "F", "Other"}
    if request.gender.upper() not in valid_genders and request.gender not in valid_genders:
        raise HTTPException(status_code=400, detail="Gender must be M, F, or Other.")

    data = PersonalInfoSchema(
        age=request.age,
        gender=request.gender,
        nationality=request.nationality.upper(),
        country_of_residence=request.country_of_residence.upper(),
        city_of_residence=request.city_of_residence.upper(),
        address=request.address.upper(),
        next_of_kin=request.next_of_kin.upper() if request.next_of_kin else None,
        next_of_kin_phone_number=request.next_of_kin_phone_number,
        patient_next_relationship=request.patient_next_relationship.upper() if request.patient_next_relationship else None,
        preferred_language=request.preferred_language.upper(),
    )

    existing = db.query(PatientPersonalInfo).filter(
        PatientPersonalInfo.patient_id == patient.id
    ).first()

    if existing:
        for k, v in data.model_dump(mode="json").items():
            setattr(existing, k, v)
        existing.updated_at = datetime.utcnow()
    else:
        record = PatientPersonalInfo(
            **data.model_dump(mode="json"),
            patient_id=patient.id,
            updated_at=datetime.utcnow(),
        )
        db.add(record)

    db.commit()
    return MessageResponse(message="Personal information saved successfully.")


@router.post("/register/medical", response_model=MessageResponse)
def save_medical_info(
    request: MedicalInfoRequest,
    db: Session = Depends(get_db),
    patient: PatientRegistration = Depends(get_current_patient),
):
    """Save / update medical information (step 3 of 3)."""
    valid_blood = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
    if request.blood_type.upper() not in valid_blood:
        raise HTTPException(status_code=400, detail=f"Blood type must be one of {', '.join(sorted(valid_blood))}.")

    data = MedicalInfoSchema(
        blood_type=request.blood_type.upper(),
        allergies=request.allergies.upper() if request.allergies else None,
        chronic_illness=request.chronic_illness.upper() if request.chronic_illness else None,
        recent_vaccination=request.recent_vaccination.upper() if request.recent_vaccination else None,
    )

    existing = db.query(PatientMedicalInfo).filter(
        PatientMedicalInfo.patient_id == patient.id
    ).first()

    if existing:
        for k, v in data.model_dump(mode="json").items():
            setattr(existing, k, v)
        existing.updated_at = datetime.utcnow()
    else:
        record = PatientMedicalInfo(
            **data.model_dump(mode="json"),
            patient_id=patient.id,
            updated_at=datetime.utcnow(),
        )
        db.add(record)

    db.commit()
    return MessageResponse(message="Medical information saved successfully.")


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    patient: PatientRegistration = Depends(get_current_patient),
):
    """Change the logged-in patient's PIN."""
    if not _check_pin(request.current_pin, patient.pin):
        raise HTTPException(status_code=401, detail="Current PIN is incorrect.")

    if request.new_pin != request.confirm_new_pin:
        raise HTTPException(status_code=400, detail="New PINs do not match.")

    if request.new_pin == request.current_pin:
        raise HTTPException(status_code=400, detail="New PIN must differ from the current PIN.")

    patient.pin = _hash_pin(request.new_pin)
    patient.updated_at = datetime.utcnow()
    db.commit()
    return MessageResponse(message="PIN updated successfully.")


@router.get("/me", response_model=TokenResponse)
def get_me(
    db: Session = Depends(get_db),
    patient: PatientRegistration = Depends(get_current_patient),
):
    """Return the current logged-in patient's profile."""
    return _build_token_response(patient, db)
