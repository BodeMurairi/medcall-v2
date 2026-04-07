from fastapi import APIRouter, Form, Depends
from fastapi.responses import PlainTextResponse

from sqlalchemy.orm import Session

from controllers.ussd.ussd_controller import handle_ussd

from database.session import get_db

router = APIRouter(prefix="/ussd", tags=["USSD"])


@router.post("", response_class=PlainTextResponse)
async def ussd_callback(
    sessionId: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(""),
    db:Session = Depends(get_db)
):

    response = handle_ussd(sessionId, text, phoneNumber, db=db)

    return PlainTextResponse(response)
