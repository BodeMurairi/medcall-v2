#!/usr/bin/env python3

from services.ussd.response import con
from services.ussd.state import USSDState, PersonalInfoMenu, MedicalInfoMenu


def main_menu(session):
    session["state"] = USSDState.MAIN_MENU
    return con(
        "Welcome to MedCall\n"
        "1. Register\n"
        "2. Personal Information\n"
        "3. Medical Information\n"
        "4. Consultation History\n"
        "0. Exit"
    )


def personal_info_submenu(session):
    session["state"] = PersonalInfoMenu.MENU
    return con(
        "Personal Information\n"
        "1. Update my details\n"
        "2. View my details\n"
        "0. Main Menu"
    )


def medical_info_submenu(session):
    session["state"] = MedicalInfoMenu.MENU
    return con(
        "Medical Information\n"
        "1. Update medical details\n"
        "2. View medical details\n"
        "0. Main Menu"
    )
