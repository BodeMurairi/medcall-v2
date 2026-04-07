#!/usr/bin/env python3

def dict_medical_info(model):
    """Turn DB Object to dict"""
    return {
        "blood_type":model.blood_type,
        "allergies":model.allergies,
        "chronic_illness":model.chronic_illness,
        "recent_vaccination":model.recent_vaccination
    }

def dict_personal_info(model):
    """Turn DB Object to dict"""
    return {
            "age":model.age,
            "gender":model.gender,
            "nationality":model.nationality,
            "country_of_residence":model.country_of_residence,
            "city_of_residence":model.city_of_residence,
            "address":model.address,
            "next_of_kin":model.next_of_kin,
            "next_of_kin_phone_number":model.next_of_kin_phone_number,
            "patient_next_relationship":model.patient_next_relationship,
            "preferred_language":model.preferred_language
        }
