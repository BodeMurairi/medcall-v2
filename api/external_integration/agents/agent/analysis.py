#!/usr/bin/env python3

import uuid
import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from external_integration.agents.utils.analysis_prompt import prompt
from external_integration.agents.tools.analysis_tool import (
    get_latest_consultation,
    web_search,
    load_east_africa_diseases_sample,
    load_health_dataset,
    load_healthcare_diseases
)

load_dotenv()

analytic_llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_G"),
    temperature=0,
    max_tokens=8000
)

analysis_ll_fallback_8 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_A"),
    temperature=0,
    max_tokens=8000
)

analytic_llm_fallback_1 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_X"),
    temperature=0,
    max_tokens=8000
)

analytic_llm_fallback_2 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_B"),
    temperature=0,
    max_tokens=8000
)

analytic_llm_fallback_3 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0,
    max_tokens=8000
)

analytic_llm_fallback_4 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_V"),
    temperature=0,
    max_tokens=8000
)

analytic_llm_fallback_5 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_F"),
    temperature=0,
    max_tokens=8000
)

analytic_llm_fallback_6 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_D"),
    temperature=0,
    max_tokens=8000
)

analytic_llm_fallback_7 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_E"),
    temperature=0,
    max_tokens=8000
)

analytic_llm_fallback_9 = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_AI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY_H"),
    temperature=0,
    max_tokens=8000
)

tools = [
    get_latest_consultation,
    web_search,
    load_healthcare_diseases,
    load_east_africa_diseases_sample,
    load_health_dataset
]

_shared_memory = InMemorySaver()

_analytic_agent = create_agent(
    model=analytic_llm,
    tools=tools,
    checkpointer=_shared_memory,
    system_prompt=prompt,
    middleware=[
        ModelFallbackMiddleware(
            analytic_llm_fallback_5,
            analytic_llm_fallback_6,
            analytic_llm_fallback_7,
            analytic_llm_fallback_1,
            analytic_llm_fallback_2,
            analytic_llm_fallback_3,
            analytic_llm_fallback_4,
            analysis_ll_fallback_8,
            analytic_llm_fallback_9
        )
    ],
    response_format=None,
)


def analytic_agent(thread_id: str = None):
    """
    Returns the pre-compiled analytic agent and a thread_id.
    The agent graph is built once at startup; per-consultation isolation
    is provided by the thread_id passed in the invoke config.
    """
    if thread_id is None:
        thread_id = str(uuid.uuid4()).split("-")[0]
    print(f"[INFO] Analytic agent with thread_id: {thread_id}")
    return _analytic_agent, thread_id
