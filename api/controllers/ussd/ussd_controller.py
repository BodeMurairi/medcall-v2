#!/usr/bin/env python3

from services.ussd.engine import ussd_engine
from sqlalchemy.orm import Session

def handle_ussd(session_id, text, phone_number, db:Session):

    return ussd_engine(session_id, text, phone_number, db=db)
