#!/usr/bin/env python3

import uuid
from pydantic import BaseModel, Field
from typing import Optional

class ConsultationRequest(BaseModel):
    phone_number: str = Field(..., description="User phone Number")
    message: str = Field(..., description="User message")
    thread_id: str = str(uuid.uuid4()).split("-")[0]

class ConsultationResponse(BaseModel):
    status: str = Field(...,description="Status of the consultation")
    message: str = Field(..., description="Doctor message")
    consultation_id: Optional[int] = None

