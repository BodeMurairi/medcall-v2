#!/usr/bin/env python3

import os
from functools import lru_cache
from langchain.tools import tool

CLINICS_DIR = os.path.join(os.path.dirname(__file__), "clinics")

COUNTRY_FILES = {
    "nigeria":     "NigeriaHospitalList.csv",
    "rwanda":      "RwandaHospitalSample.csv",
    "kenya":       "KenyaHospitalSample.csv",
    "uganda":      "UgandaHospitalSamples.csv",
    "tanzania":    "TanzaniaHospitalSamples.csv",
    "ethiopia":    "EhtiopiaHospitalSample.csv",
    "egypt":       "EgyptHospitalSample.csv",
    "sudan":       "SudanHospitalSample.csv",
    "south sudan": "SouthSudanHospitalSamples.csv",
}


@lru_cache(maxsize=8)
def _load_clinic_data(country_key: str) -> str:
    filename = COUNTRY_FILES.get(country_key)
    if not filename:
        available = ", ".join(COUNTRY_FILES.keys())
        return f"No clinic data available for '{country_key}'. Supported countries: {available}."
    path = os.path.join(CLINICS_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"Error loading clinic data for '{country_key}': {e}"


@tool
def load_clinics_by_country(country: str) -> str:
    """
    This tool loads all healthcare facilities, hospitals, clinics, pharmacies, and specialists
    for a given East African or North African country.
    Use this to find referral facilities near the patient's location.
    Supported countries: Nigeria, Rwanda, Kenya, Uganda, Tanzania, Ethiopia, Egypt, Sudan, South Sudan.

    Args:
        country: Name of the country (case-insensitive).

    Returns:
        Full list of healthcare providers with names, locations, and services.
    """
    return _load_clinic_data(country.strip().lower())


@tool
def load_all_clinics() -> str:
    """
    This tooLoad healthcare facilities for ALL supported countries at once.
    Use this when the patient's country is unknown or when a broad search is needed.
    Covers: Nigeria, Rwanda, Kenya, Uganda, Tanzania, Ethiopia, Egypt, Sudan, South Sudan.

    Returns:
        Combined healthcare provider data for all countries.
    """
    sections = []
    for country_key, filename in COUNTRY_FILES.items():
        data = _load_clinic_data(country_key)
        sections.append(f"=== {country_key.upper()} ===\n{data}")
    return "\n\n".join(sections)
