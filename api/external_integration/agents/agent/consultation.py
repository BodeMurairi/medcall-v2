#!/usr/bin/env python3

import uuid
import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from external_integration.agents.utils.prompts import consultation_prompt
from external_integration.agents.tools.consultation_tool import (
    verify_registration,
    collect_user_personal_info,
    collect_medical_information
)

load_dotenv()

consultation_llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_G"),
    temperature=0.1,
    max_tokens=8000
)

consultation_llm_fallback_8 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_A"),
    temperature=0.1,
    max_tokens=8000
)

consultation_llm_fallback_1 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_X"),
    temperature=0.1,
    max_tokens=8000
)

consultation_llm_fallback_2 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_B"),
    temperature=0.1,
    max_tokens=8000
)

consultation_llm_fallback_3 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1,
    max_tokens=8000
)

consultation_llm_fallback_4 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_V"),
    temperature=0.1,
    max_tokens=8000
)

consultation_llm_fallback_5 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_F"),
    temperature=0.1,
    max_tokens=8000
)

consultation_llm_fallback_6 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_D"),
    temperature=0.1,
    max_tokens=8000
)

consultation_llm_fallback_7 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_E"),
    temperature=0.1,
    max_tokens=8000
)

consultation_llm_fallback_9 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_H"),
    temperature=0.1,
    max_tokens=8000
)

memory_thread = {
    "memory_id": str(uuid.uuid4()).split("-")[0],
    "memory": InMemorySaver()
}

tools = [verify_registration, collect_user_personal_info, collect_medical_information]


def consultation_agent():
    """consultation agent"""
    return create_agent(
        model=consultation_llm,
        tools=tools,
        checkpointer=memory_thread["memory"],
        system_prompt=consultation_prompt,
        middleware=[
            ModelFallbackMiddleware(
                consultation_llm_fallback_5,
                consultation_llm_fallback_6,
                consultation_llm_fallback_7,
                consultation_llm_fallback_1,
                consultation_llm_fallback_2,
                consultation_llm_fallback_3,
                consultation_llm_fallback_4,
                consultation_llm_fallback_8,
                consultation_llm_fallback_9
            )
        ],
        response_format=None,
    )
