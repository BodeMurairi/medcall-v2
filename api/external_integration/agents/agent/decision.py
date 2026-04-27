#!/usr/bin/env python3

import uuid
import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from external_integration.agents.tools.consultation_tool import collect_user_personal_info, collect_medical_information
from external_integration.agents.tools.analysis_tool import (
    web_search
    )

from external_integration.agents.tools.clinic_tool import (
    load_clinics_by_country,
    load_all_clinics
)
from external_integration.agents.utils.decision_prompt import prompt

load_dotenv()

decision_llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_G"),
    temperature=0,
    max_tokens=16000
)

decision_llm_fallback_8 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_A"),
    temperature=0,
    max_tokens=16000
)

decision_llm_fallback_1 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_X"),
    temperature=0,
    max_tokens=16000
)

decision_llm_fallback_2 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_B"),
    temperature=0,
    max_tokens=16000
)

decision_llm_fallback_3 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0,
    max_tokens=16000
)

decision_llm_fallback_4 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_V"),
    temperature=0,
    max_tokens=16000
)

decision_llm_fallback_5 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_F"),
    temperature=0,
    max_tokens=16000
)

decision_llm_fallback_6 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_D"),
    temperature=0,
    max_tokens=16000
)

decision_llm_fallback_7 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_E"),
    temperature=0,
    max_tokens=16000
)

decision_llm_fallback_9 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_H"),
    temperature=0,
    max_tokens=16000
)

tools = [
    web_search,
    load_clinics_by_country,
    load_all_clinics,
    collect_user_personal_info,
    collect_medical_information
    ]

_shared_memory = InMemorySaver()

_decision_agent = create_agent(
    model=decision_llm,
    tools=tools,
    checkpointer=_shared_memory,
    system_prompt=prompt,
    middleware=[
        ModelFallbackMiddleware(
            decision_llm_fallback_5,
            decision_llm_fallback_6,
            decision_llm_fallback_7,
            decision_llm_fallback_1,
            decision_llm_fallback_2,
            decision_llm_fallback_3,
            decision_llm_fallback_4,
            decision_llm_fallback_9
        )
    ],
    response_format=None,
)


def decision_agent(thread_id: str = None):
    """
    This function returns the precompiled decision agent
    """
    if thread_id is None:
        thread_id = str(uuid.uuid4()).split("-")[0]
    print(f"[INFO] decision agent with thread_id: {thread_id}")
    return _decision_agent, thread_id
