#!/usr/bin/env python3
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

# Patient Registration Model
class PatientRegistration(BaseModel):
    first_name: str = Field(..., description="Patient first name")
    last_name: str = Field(..., description="Patient last name")
    phone_number: str = Field(..., description="Patient phone number, digits only, e.g., +2507XXXXXXX", min_length=10, max_length=15)
    email_address: Optional[EmailStr] = Field(None, description="Patient email address")
    pin: str = Field(..., description="Patient unique PIN for USSD authentication min_vaue is 6", examples="000000")

# Patient Personal Info Model
class PatientPersonalInfo(BaseModel):
    age: int = Field(..., description="Patient age")
    gender: str = Field(..., description="Patient gender: M, F, or OTHER")
    nationality: str = Field(..., description="Patient nationality")
    country_of_residence: str = Field(..., description="Country of residence")
    city_of_residence: str = Field(..., description="City of residence")
    address: str = Field(..., description="Patient address")
    next_of_kin: Optional[str] = Field(None, description="Patient next of kin name")
    next_of_kin_phone_number: Optional[str] = Field(None, description="Next of kin phone number")
    patient_next_relationship: Optional[str] = Field(None, description="Relationship with next of kin")
    preferred_language: str = Field(..., description="Preferred language for communication")

    @field_validator("next_of_kin_phone_number")
    def validate_next_of_kin_phone(cls, value):
        if value is not None and not value.isdigit():
            raise ValueError("Next of kin phone number must contain digits only")
        return value

    @field_validator("gender")
    def validate_gender(cls, value):
        if value not in {"M", "F", "Other"}:
            raise ValueError("Gender must be M, F, or Other")
        return value


# Patient Medical Info Model
class PatientMedicalInformation(BaseModel):
    blood_type: str = Field(..., description="Patient blood type, e.g., A+, O-")
    allergies: Optional[str] = Field(None, description="Patient allergies")
    chronic_illness: Optional[str] = Field(None, description="Any chronic illnesses")
    recent_vaccination: Optional[str] = Field(None, description="Recent vaccinations")

    @field_validator("blood_type")
    def validate_blood_type(cls, value):
        valid_types = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
        if value not in valid_types:
            raise ValueError(f"Blood type must be one of {valid_types}")
        return value
