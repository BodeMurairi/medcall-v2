#!/usr/bin/env python3

from pydantic import BaseModel, Field, ConfigDict, field_validator

class InboundSMS(BaseModel):
    """
    Inbound SMS webhook payload from SMSGateway24 (form-encoded).
    Aliases map the gateway's field names to Python-friendly names.
    """
    model_config = ConfigDict(populate_by_name=True)

    messageId:   str        = Field(..., alias="sms_id",      description="Gateway's unique SMS ID.")
    phoneNumber: str        = Field(..., alias="address",     description="Sender's phone number.")
    message:     str        = Field(..., alias="body",        description="SMS body text.")
    receivedAt:  str        = Field(..., alias="date",        description="Timestamp the message was received.")
    deviceId:    str | None = Field(None, alias="device_id")
    deviceName:  str | None = Field(None, alias="device_name")
    simNumber:   int | None = Field(None, alias="sim")
    internalId:  str | None = Field(None, alias="internal_id")

    @field_validator("phoneNumber", mode="before")
    @classmethod
    def fix_phone_number(cls, v: str) -> str:
        """
        Form-encoded data decodes '+' as a space.
        Restore the leading '+' if the number begins with a space
        followed by digits (i.e. an international number).
        """
        if isinstance(v, str) and v.startswith(" "):
            v = "+" + v.lstrip()
        return v.strip()