#!/usr/bin/env python3

from services.ussd.response import con
from services.ussd.state import USSDState

def main_menu(session):

    session["state"] = USSDState.MAIN_MENU

    return con(
        "Welcome to MedCall\n"
        "1. Register as patient\n"
        "2. Register Your Personal Information\n"
        "3. Register Your Medical Information\n"
        "4. View Your Medical Information\n"
        "5. View Your Personal Information\n"
        "6. View Consultations History\n"
        "7. Subscription\n"       
        "8. Quit"
    )
