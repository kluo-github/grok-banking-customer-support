import re
import secrets

from database import ticket_exists


def generate_unique_ticket_number():
    while True:
        number = secrets.randbelow(900000) + 100000
        ticket_number = str(number)

        if not ticket_exists(ticket_number):
            return ticket_number


def extract_ticket_number(message):
    """
    Extract a 6-digit ticket number from the customer message.
    """

    match = re.search(r"\b\d{6}\b", message)

    if match:
        return match.group()

    return None