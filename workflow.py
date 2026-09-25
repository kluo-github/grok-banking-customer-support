from crewai import Crew, Task, Process

from agents import (
    create_classifier_agent,
    create_feedback_agent,
    create_query_agent
)

from database import (
    create_ticket,
    get_ticket,
    log_interaction
)

from tools import (
    generate_unique_ticket_number,
    extract_ticket_number
)

from logger_config import logger


VALID_CLASSIFICATIONS = {
    "POSITIVE_FEEDBACK",
    "NEGATIVE_FEEDBACK",
    "QUERY"
}


def run_single_agent(agent, task_description, expected_output):
    task = Task(
        description=task_description,
        expected_output=expected_output,
        agent=agent
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )

    result = crew.kickoff()

    if hasattr(result, "raw"):
        return result.raw.strip()

    return str(result).strip()


def classify_message(message):
    classifier = create_classifier_agent()

    prompt = f"""
You are the first agent in a banking customer support system.

Analyze this customer message:

"{message}"

Classify the message into EXACTLY ONE of the following categories:

POSITIVE_FEEDBACK
- Customer is expressing thanks, satisfaction, appreciation, or praise.

NEGATIVE_FEEDBACK
- Customer is complaining, frustrated, disappointed, reporting a problem,
  or describing something that has not been resolved.

QUERY
- Customer is asking for information, especially requesting the status
  of an existing support ticket.

IMPORTANT:
Return ONLY one of these exact values:

POSITIVE_FEEDBACK
NEGATIVE_FEEDBACK
QUERY

Do not return explanations.
"""

    result = run_single_agent(
        classifier,
        prompt,
        "Exactly one classification label."
    )

    result = result.upper().strip()

    for classification in VALID_CLASSIFICATIONS:
        if classification in result:
            return classification

    logger.error(
        "Classifier returned unexpected result: %s",
        result
    )

    return "QUERY"


def handle_positive_feedback(customer_name, message):
    feedback_agent = create_feedback_agent()

    prompt = f"""
A banking customer named {customer_name} provided positive feedback.

Customer message:

"{message}"

Generate a short, warm and professional thank-you message.

Requirements:
- Address the customer by name.
- Thank the customer.
- Be warm but professional.
- Keep the response to 1 or 2 sentences.
- Do not create a support ticket.
"""

    response = run_single_agent(
        feedback_agent,
        prompt,
        "A short personalized customer thank-you response."
    )

    log_interaction(
        customer_name=customer_name,
        user_message=message,
        classification="POSITIVE_FEEDBACK",
        agent_used="Feedback Handler Agent",
        response=response,
        action="No database action",
        success=True
    )

    logger.info(
        "Positive feedback handled for customer %s",
        customer_name
    )

    return {
        "classification": "POSITIVE_FEEDBACK",
        "agent": "Feedback Handler Agent",
        "response": response,
        "ticket_number": None,
        "database_action": "No ticket created",
        "success": True
    }


def handle_negative_feedback(customer_name, message):
    feedback_agent = create_feedback_agent()

    ticket_number = generate_unique_ticket_number()

    create_ticket(
        ticket_number=ticket_number,
        customer_name=customer_name,
        message=message
    )

    prompt = f"""
A banking customer named {customer_name} reported a negative experience.

Customer message:

"{message}"

A support ticket has already been created.

Ticket number:
{ticket_number}

Generate a short empathetic banking customer service response.

Requirements:
- Apologize for the inconvenience.
- Acknowledge the customer's concern.
- Tell the customer that ticket #{ticket_number} has been created.
- Tell them the support team will follow up.
- DO NOT change or invent another ticket number.
- Keep the response concise.
"""

    response = run_single_agent(
        feedback_agent,
        prompt,
        (
            "An empathetic response containing the exact "
            f"ticket number #{ticket_number}."
        )
    )

    log_interaction(
        customer_name=customer_name,
        user_message=message,
        classification="NEGATIVE_FEEDBACK",
        agent_used="Feedback Handler Agent",
        response=response,
        ticket_number=ticket_number,
        action="New unresolved ticket created",
        success=True
    )

    logger.info(
        "Ticket %s created for %s",
        ticket_number,
        customer_name
    )

    return {
        "classification": "NEGATIVE_FEEDBACK",
        "agent": "Feedback Handler Agent",
        "response": response,
        "ticket_number": ticket_number,
        "database_action": (
            f"Ticket #{ticket_number} created with status Unresolved"
        ),
        "success": True
    }


def handle_query(customer_name, message):
    query_agent = create_query_agent()

    ticket_number = extract_ticket_number(message)

    if not ticket_number:
        response = (
            "I could not find a valid 6-digit ticket number in your message. "
            "Please provide your ticket number so I can check its status."
        )

        log_interaction(
            customer_name=customer_name,
            user_message=message,
            classification="QUERY",
            agent_used="Query Handler Agent",
            response=response,
            action="Ticket number not found in message",
            success=False
        )

        return {
            "classification": "QUERY",
            "agent": "Query Handler Agent",
            "response": response,
            "ticket_number": None,
            "database_action": "No database record queried",
            "success": False
        }

    ticket = get_ticket(ticket_number)

    if not ticket:
        response = (
            f"I couldn't find ticket #{ticket_number}. "
            "Please verify the ticket number and try again."
        )

        log_interaction(
            customer_name=customer_name,
            user_message=message,
            classification="QUERY",
            agent_used="Query Handler Agent",
            response=response,
            ticket_number=ticket_number,
            action="Ticket lookup failed",
            success=False
        )

        return {
            "classification": "QUERY",
            "agent": "Query Handler Agent",
            "response": response,
            "ticket_number": ticket_number,
            "database_action": "Ticket not found",
            "success": False
        }

    status = ticket["status"]

    prompt = f"""
A banking customer named {customer_name} is asking about an existing
support ticket.

Customer message:

"{message}"

Ticket number:
{ticket_number}

Current database status:
{status}

Generate a concise response telling the customer the current ticket status.

Requirements:
- Use ticket number #{ticket_number}.
- State the exact status: {status}.
- Do not change or invent the status.
- Be professional and concise.

Example format:
"Your ticket #123456 is currently marked as: Resolved."
"""

    response = run_single_agent(
        query_agent,
        prompt,
        (
            f"A short ticket status response containing "
            f"ticket #{ticket_number} and status {status}."
        )
    )

    log_interaction(
        customer_name=customer_name,
        user_message=message,
        classification="QUERY",
        agent_used="Query Handler Agent",
        response=response,
        ticket_number=ticket_number,
        action="Ticket status retrieved",
        success=True
    )

    logger.info(
        "Ticket %s queried successfully",
        ticket_number
    )

    return {
        "classification": "QUERY",
        "agent": "Query Handler Agent",
        "response": response,
        "ticket_number": ticket_number,
        "database_action": (
            f"Retrieved status '{status}' for ticket #{ticket_number}"
        ),
        "success": True
    }


def process_customer_message(customer_name, message):
    logger.info(
        "Processing message from %s: %s",
        customer_name,
        message
    )

    classification = classify_message(message)

    if classification == "POSITIVE_FEEDBACK":
        return handle_positive_feedback(
            customer_name,
            message
        )

    if classification == "NEGATIVE_FEEDBACK":
        return handle_negative_feedback(
            customer_name,
            message
        )

    if classification == "QUERY":
        return handle_query(
            customer_name,
            message
        )

    return {
        "classification": "UNKNOWN",
        "agent": "None",
        "response": "Unable to process the request.",
        "ticket_number": None,
        "database_action": "None",
        "success": False
    }