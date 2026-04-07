#!/usr/bin/env python3

import uuid
import json
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy import JSON
from database.base import Base

def generate_patient_code():
    return str(uuid.uuid4()).split('-')[0]

# Patient Registration
class PatientRegistration(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String, default=lambda: f"Patient-{generate_patient_code()}", unique=True, nullable=False)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    email_address = Column(String, nullable=True)
    pin = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    personal_info = relationship(
        "PatientPersonalInfo",
        back_populates="patient",
        uselist=False,
        cascade="all, delete-orphan"
    )

    medical_info = relationship(
        "PatientMedicalInfo",
        back_populates="patient",
        uselist=False,
        cascade="all, delete-orphan"
    )

    consultations = relationship(
        "Consultation",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

# Patient Personal Info
class PatientPersonalInfo(Base):
    __tablename__ = "patient_personal_info"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), unique=True, nullable=False)
    info_id = Column(String, default=lambda: generate_patient_code(), unique=True, nullable=False)

    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    nationality = Column(String, nullable=False)
    country_of_residence = Column(String, nullable=False)
    city_of_residence = Column(String, nullable=False)
    address = Column(String, nullable=False)

    next_of_kin = Column(String, nullable=True)
    next_of_kin_phone_number = Column(String, nullable=True)
    patient_next_relationship = Column(String, nullable=True)
    preferred_language = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("PatientRegistration", back_populates="personal_info")

# Patient Medical Info
class PatientMedicalInfo(Base):
    __tablename__ = "patient_medical_info"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), unique=True, nullable=False)
    info_id = Column(String, default=lambda: generate_patient_code(), unique=True, nullable=False)

    blood_type = Column(String, nullable=False)
    allergies = Column(Text, nullable=True)
    chronic_illness = Column(Text, nullable=True)
    recent_vaccination = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("PatientRegistration", back_populates="medical_info")

# Consultation
class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    consultation_id = Column(String, default=lambda: f"consul-{generate_patient_code()}", unique=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    risk_level = Column(JSON, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    consultation_summary = Column(Text, nullable=True)
    consultation_status = Column(Boolean, default=True, nullable=False)
    thread_id = Column(String, nullable=True)
    patient = relationship("PatientRegistration", back_populates="consultations")
    consultation_sms = relationship("ConsultationSMS",
                                    back_populates="consultation",
                                    cascade="all, delete-orphan",
                                    order_by="ConsultationSMS.timestamp"
                                    )
    referrals = relationship("Referral",
                             back_populates="consultation",
                             cascade="all, delete-orphan"
                             )
    analysis = relationship(
        "ConsultationAnalysis",
        back_populates="consultation",
        cascade="all, delete-orphan",
        uselist=False
        )
    decision = relationship(
        "ConsultationDecision",
        back_populates="consultation",
        cascade="all, delete-orphan",
        uselist=False
        )

# Consultation SMS
class ConsultationSMS(Base):
    __tablename__ = "consultation_sms"

    id = Column(Integer, primary_key=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    sms_id = Column(String, default=lambda: generate_patient_code(), nullable=False)
    message_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    sms_metadata = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    consultation = relationship("Consultation",
                                back_populates="consultation_sms"
                                )


class ConsultationAnalysis(Base):
    __tablename__ = "consultation_analysis"

    id = Column(String, primary_key=True, default=lambda: f"analysis-{generate_patient_code()}")
    consultation_id = Column(Integer, ForeignKey("consultations.id", ondelete="CASCADE"), nullable=False)

    detected_symptoms = Column(TEXT, nullable=False)
    possible_conditions = Column(TEXT, nullable=False)
    exams = Column(TEXT, nullable=False)

    risk_level = Column(String, nullable=False)
    mark_emergency = Column(Boolean, default=False)
    reasoning = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    consultation = relationship("Consultation", back_populates="analysis")

    def set_detected_symptoms(self, data):
        self.detected_symptoms = json.dumps(data)

    def get_detected_symptoms(self):
        return json.loads(self.detected_symptoms or "[]")

    def set_possible_conditions(self, data):
        self.possible_conditions = json.dumps(data)

    def get_possible_conditions(self):
        return json.loads(self.possible_conditions or "[]")

    def set_exams(self, data):
        self.exams = json.dumps(data)

    def get_exams(self):
        return json.loads(self.exams or "{}")

# Consultation Decision
class ConsultationDecision(Base):
    __tablename__ = "consultation_decisions"

    id = Column(String, primary_key=True, default=lambda: f"decision-{generate_patient_code()}")
    consultation_id = Column(Integer, ForeignKey("consultations.id", ondelete="CASCADE"), nullable=False, unique=True)

    message = Column(Text, nullable=False)
    urgency = Column(String, nullable=False)
    action = Column(String, nullable=False)
    referral_type = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    consultation = relationship("Consultation", back_populates="decision")


# Referral
class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    referral_id = Column(String, default=lambda: f"referral-{generate_patient_code()}", unique=True, nullable=False)
    reason = Column(Text, nullable=False)
    referral_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    consultation = relationship("Consultation", back_populates="referrals")
    facility = relationship("Facility", uselist=False, back_populates="referral")

# Facilities
class Facility(Base):
    __tablename__ = "clinic_facilities"

    id = Column(Integer, primary_key=True)
    facility_id = Column(String, default=lambda: f"facility-{generate_patient_code()}", unique=True)
    name = Column(String, nullable=False)
    location = Column(Text, nullable=True)
    services = Column(Text, nullable=True)

    referral_id = Column(Integer, ForeignKey("referrals.id"), unique=True)
    referral = relationship("Referral", back_populates="facility")

# System Log
class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True)
    action_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    performed_by = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
