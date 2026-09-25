import sqlite3
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "banking_support.db"


def get_connection():
    DATA_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT UNIQUE NOT NULL,
            customer_name TEXT,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'Unresolved',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interaction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            user_message TEXT NOT NULL,
            classification TEXT,
            agent_used TEXT,
            response TEXT,
            ticket_number TEXT,
            action TEXT,
            success INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def ticket_exists(ticket_number):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT ticket_number FROM support_tickets WHERE ticket_number = ?",
        (ticket_number,)
    )

    result = cursor.fetchone()
    connection.close()

    return result is not None


def create_ticket(ticket_number, customer_name, message):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO support_tickets (
            ticket_number,
            customer_name,
            message,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        ticket_number,
        customer_name,
        message,
        "Unresolved",
        now,
        now
    ))

    connection.commit()
    connection.close()


def get_ticket(ticket_number):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM support_tickets
        WHERE ticket_number = ?
    """, (ticket_number,))

    row = cursor.fetchone()
    connection.close()

    if row:
        return dict(row)

    return None


def get_all_tickets():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM support_tickets
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def update_ticket_status(ticket_number, new_status):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE support_tickets
        SET status = ?,
            updated_at = ?
        WHERE ticket_number = ?
    """, (
        new_status,
        now,
        ticket_number
    ))

    connection.commit()

    updated = cursor.rowcount > 0
    connection.close()

    return updated


def log_interaction(
    customer_name,
    user_message,
    classification,
    agent_used,
    response,
    ticket_number=None,
    action=None,
    success=True
):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO interaction_logs (
            customer_name,
            user_message,
            classification,
            agent_used,
            response,
            ticket_number,
            action,
            success,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_name,
        user_message,
        classification,
        agent_used,
        response,
        ticket_number,
        action,
        1 if success else 0,
        now
    ))

    connection.commit()
    connection.close()


def get_all_logs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM interaction_logs
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]