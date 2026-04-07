#!/usr/bin/env python3

from sqlalchemy.orm import Session
from models.database_models import PatientRegistration
from services.ussd.response import con, end

def search_user(db:Session, phone_number, model):
    """Search within database"""
    existing_user = db.query(
        model).where(
            model.phone_number == phone_number).first()
    
    if not existing_user:
        return end("User not found. Register first before using MedCall")

    return existing_user

def search_patient_data(db:Session, model, patient_id):
    """Search patient information"""
    patient_data = db.query(model).where(model.patient_id == patient_id)
    if not patient_data:
        return None
    return patient_data

def search_list_patient_data(db:Session, model, patient_id):
    """Search patient information"""
    patient_data = db.query(model).where(model.patient_id == patient_id).all()
    if not patient_data:
        return 
    return patient_data
