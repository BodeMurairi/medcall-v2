#!/usr/bin/env python3

import os
import json
from pathlib import Path
import pandas as pd
from functools import lru_cache
from typing import Dict, Any, Union, List

from tavily import TavilyClient
from dotenv import load_dotenv

from models.database_models import PatientRegistration, Consultation, ConsultationSMS
from database.create_session import SessionLocal

from langchain.tools import tool
from external_integration.agents.utils.convert_to_dict import to_dict

load_dotenv()

# Base directory relative to this file — datasets live in the same folder
BASE_DIR = Path(__file__).parent / "healthdatasets"


# Database tool — creates its own session (agents cannot inject db sessions)
@tool
def get_latest_consultation(patient_id: str) -> Dict[str, Any]:
    """
    Fetches the latest completed consultation for a registered patient
    along with its conversation SMS history.
    Args:
        patient_id: The patient's string ID (e.g. 'Patient-abc123')
    """
    db = SessionLocal()
    try:
        patient = db.query(PatientRegistration).filter(
            PatientRegistration.patient_id == patient_id
        ).first()
        if not patient:
            return {"error": f"No patient found with ID {patient_id}"}

        consultation = (
            db.query(Consultation)
            .filter(
                Consultation.patient_id == patient.id,
                Consultation.consultation_status == False
            )
            .order_by(Consultation.last_updated.desc())
            .first()
        )
        if not consultation:
            return {"error": f"No completed consultation found for patient {patient_id}"}

        sms_list = db.query(ConsultationSMS).filter(
            ConsultationSMS.consultation_id == consultation.id
        ).all()

        return {
            "patient_id": patient_id,
            "consultation": to_dict(consultation),
            "conversation": [to_dict(sms) for sms in sms_list]
        }
    finally:
        db.close()


# Dataset tools with caching
@tool
@lru_cache(maxsize=3)
def load_health_dataset() -> Union[Dict[str, Any], str]:
    """
    Loads worldwide disease dataset with symptoms (columns: disease, symptoms 1-12).
    Uses caching to prevent repeated file reads.
    """
    file_path = BASE_DIR / "health_dataset.csv"
    if not file_path.exists():
        return f"Health dataset not found at {file_path}"

    try:
        data = pd.read_csv(file_path, engine="python")
        return data.fillna("").head(60).to_dict(orient="records")
    except Exception as error:
        return f"Error loading dataset:\n{error}"


@tool
@lru_cache(maxsize=3)
def load_healthcare_diseases() -> Union[Dict[str, Any], str]:
    """
    Loads a comprehensive healthcare dataset from HuggingFace
    (treatments, symptoms, risk factors, complications, prevention).
    """
    file_path = BASE_DIR / "healthcare_diseases_dataset_huggingface.csv"
    if not file_path.exists():
        return f"Healthcare dataset not found at {file_path}"

    try:
        data = pd.read_csv(file_path, engine="python")
        return data.fillna("").head(60).to_dict(orient="records")
    except Exception as error:
        return f"Error loading healthcare diseases dataset:\n{error}"


@tool
@lru_cache(maxsize=3)
def load_east_africa_diseases_sample() -> Union[List[Dict[str, Any]], str]:
    """
    Loads a sample dataset of recurring diseases in East Africa (AFRICACDC).
    """
    file_path = BASE_DIR / "east_africa_diseases_sample.json"
    if not file_path.exists():
        return f"East Africa diseases sample not found at {file_path}"

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        for disease in data:
            for key in ["disease", "description", "symptoms", "recommended_exams"]:
                if key not in disease:
                    return f"Dataset validation error: missing '{key}' in one entry"
        return data
    except Exception as error:
        return f"Error loading East Africa diseases sample:\n{error}"


# Web search tool
@tool
def web_search(question: str) -> Union[Dict[str, Any], str]:
    """
    Web search powered by Tavily API.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "No Tavily API key provided. Cannot perform web search."

    try:
        client = TavilyClient(api_key=api_key)
        return client.search(query=question)
    except Exception as e:
        return f"Web search failed: {e}"
