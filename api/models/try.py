from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid
import json

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class ConsultationAnalysis(Base):
    __tablename__ = "consultation_analysis"

    id = Column(String, primary_key=True, default=generate_uuid)
    consultation_id = Column(String, ForeignKey("consultation.id", ondelete="CASCADE"), nullable=False)

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
