import os

import crewai.llms.cache as _crewai_cache

# Workaround for CrewAI cache_breakpoint bug with Groq
_crewai_cache.mark_cache_breakpoint = lambda msg: msg

from dotenv import load_dotenv
from crewai import Agent, LLM

load_dotenv(".env")


def get_llm():
    model_name = os.getenv(
        "LLM_MODEL",
        "groq/openai/gpt-oss-20b"
    )

    return LLM(
        model=model_name,
        temperature=0.2
    )

def create_classifier_agent():
    return Agent(
        role="Banking Customer Message Classifier",

        goal=(
            "Accurately classify banking customer messages into "
            "POSITIVE_FEEDBACK, NEGATIVE_FEEDBACK, or QUERY."
        ),

        backstory=(
            "You are an experienced banking customer support specialist. "
            "You carefully analyze customer intent and sentiment. "
            "You identify whether a customer is expressing positive feedback, "
            "negative feedback, or asking a support query."
        ),

        llm=get_llm(),

        verbose=True,

        allow_delegation=False
    )


def create_feedback_agent():
    return Agent(
        role="Banking Feedback Support Specialist",

        goal=(
            "Respond professionally and empathetically to banking customer "
            "feedback while maintaining a friendly and helpful tone."
        ),

        backstory=(
            "You are a banking customer service professional known for empathy, "
            "professionalism, and excellent communication. "
            "For positive feedback, you thank customers warmly. "
            "For negative feedback, you acknowledge the problem and reassure "
            "customers that their support issue will be addressed."
        ),

        llm=get_llm(),

        verbose=True,

        allow_delegation=False
    )


def create_query_agent():
    return Agent(
        role="Banking Ticket Query Specialist",

        goal=(
            "Help banking customers understand the current status of their "
            "support tickets clearly and professionally."
        ),

        backstory=(
            "You specialize in banking support ticket inquiries. "
            "You communicate ticket information clearly and concisely "
            "without changing factual ticket status information."
        ),

        llm=get_llm(),

        verbose=True,

        allow_delegation=False
    )


def create_evaluator_agent():
    return Agent(
        role="Banking AI Quality Evaluator",

        goal=(
            "Evaluate banking customer service responses for empathy, clarity, "
            "professionalism, and relevance."
        ),

        backstory=(
            "You are a quality assurance specialist responsible for evaluating "
            "AI-generated banking customer support responses."
        ),

        llm=get_llm(),

        verbose=False,

        allow_delegation=False
    )