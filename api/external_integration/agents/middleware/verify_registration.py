#!/usr/bin/env python3
import json
from langchain.agents.middleware import BaseAgentMiddleware
from external_integration.agents.tools.consultation_tool import verify_registration

class VerifyRegistrationMiddleware(BaseAgentMiddleware):
    """
    Middleware to check registration before any agent processing.
    """

    async def on_chain_start(self, inputs: dict, **kwargs) -> dict:
        """
        Called when the agent chain starts. Stops the agent if the user is not registered.
        """
        messages = inputs.get("messages", [])
        if messages:
            last_msg = messages[-1].content
            phone_number = None
            if "user phone number:" in last_msg:
                phone_number = last_msg.split("user phone number:")[-1].strip()

            if phone_number:
                result = verify_registration.invoke({"phone_number": phone_number})
                if not result.get("registered", False):
                    # Inject a system message to end consultation
                    messages.append({
                        "type": "system",
                        "content": json.dumps({
                            "status": "complete",
                            "current_message": "Sorry! You are not registered. Please use *384*41992# to register.",
                            "tool_call": {},
                            "consultation_sms": [],
                            "doctor_questions": [],
                            "patient_responses": [],
                            "collected_data": {},
                            "summary": "User not registered"
                        })
                    })
                    # Stop further processing by raising a signal
                    raise RuntimeError("User not registered, stopping agent.")

        return inputs
