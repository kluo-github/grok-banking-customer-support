# grok-banking-customer-support

Please also read BankingCustomerSupportWriteUp.docx for description about the project.

# Banking Customer Support AI Agent

A multi-agent Generative AI application for banking customer support built with **Python, CrewAI, Groq, SQLite, and Streamlit**.

The system classifies incoming customer messages, routes them to the appropriate AI agent, generates personalized responses, creates and tracks support tickets, stores interaction logs, and provides an evaluation dashboard.

---

## Project Overview

Modern digital banking platforms receive large volumes of customer support requests. Traditional support systems may require significant manual effort to classify messages, respond to customers, create tickets, and provide ticket-status updates.

This project demonstrates a **multi-agent AI architecture** that automates these workflows while keeping important transactional operations, such as ticket creation and database updates, deterministic and controlled by Python.

The application supports three main customer interaction types:

- **Positive Feedback**
- **Negative Feedback**
- **Ticket Status Queries**

---

## Features

### Classifier Agent

The CrewAI Classifier Agent analyzes an incoming customer message and classifies it as:

```text
POSITIVE_FEEDBACK
NEGATIVE_FEEDBACK
QUERY
```

The classification result determines which downstream agent handles the request.

### Feedback Handler Agent

For positive feedback, the agent generates a personalized thank-you message.

Example:

```text
Customer:
Thanks for resolving my credit card issue.

Classification:
POSITIVE_FEEDBACK

Response:
Thank you for your kind words! We're delighted that we could assist you.
```

For negative feedback, the system:

1. Generates a unique six-digit ticket number
2. Creates a ticket in the SQLite database
3. Sets the initial status to `Unresolved`
4. Generates an empathetic response

Example:

```text
Customer:
My debit card replacement still hasn't arrived.

Classification:
NEGATIVE_FEEDBACK

Response:
We apologize for the inconvenience. A new ticket #483921 has been
created, and our support team will follow up shortly.
```

### Query Handler Agent

The Query Handler extracts a six-digit ticket number from the customer message and searches the SQLite database.

Example:

```text
Customer:
Can you check the status of ticket 483921?

Response:
Your ticket #483921 is currently marked as: Unresolved.
```

### Ticket Management

The application provides an interface to:

- View support tickets
- View the original customer issue
- View ticket creation dates
- Change ticket status
- Track `Unresolved`, `In Progress`, and `Resolved` tickets

### Logging

Customer interactions are stored in the database for debugging and LLMOps analysis.

Logs include:

- Customer name
- Customer message
- Classification
- Agent used
- AI response
- Ticket number
- Database action
- Success/failure status
- Timestamp

### Model Evaluation

The application includes predefined test cases for evaluating the Classifier Agent.

The evaluation dashboard displays:

- Total test cases
- Passed test cases
- Failed test cases
- Classification accuracy
- Expected classification
- Actual classification

---

# System Architecture

```text
                         Customer Message
                                |
                                v
                      +-------------------+
                      | Classifier Agent  |
                      |      CrewAI       |
                      +---------+---------+
                                |
              +-----------------+------------------+
              |                 |                  |
              v                 v                  v
      Positive Feedback  Negative Feedback       Query
              |                 |                  |
              v                 v                  v
       Feedback Agent    Feedback Agent      Query Agent
                                |                  |
                                v                  v
                         Create Ticket        Lookup Ticket
                                |                  |
                                +--------+---------+
                                         |
                                         v
                                  SQLite Database
```

CrewAI handles natural-language reasoning and response generation.

Python handles deterministic operations such as:

- Message routing
- Ticket-number generation
- Ticket extraction
- Database inserts
- Database lookups
- Ticket-status updates
- Logging

This design prevents the language model from directly controlling transactional database operations.

---

# Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Multi-Agent Framework | CrewAI |
| LLM Provider | Groq |
| LLM Integration | LiteLLM |
| Current Model | `openai/gpt-oss-20b` |
| Web Interface | Streamlit |
| Database | SQLite |
| Database GUI | DB Browser for SQLite |
| Data Handling | Pandas |
| Environment Variables | python-dotenv |
| IDE | Visual Studio Code |
| Operating System Used | Fedora Linux 43 |

---

# Development Environment

This project was developed using:

```text
Operating System: Fedora Linux 43
IDE: Visual Studio Code
Python: 3.12
Database: SQLite
Database GUI: DB Browser for SQLite
```

Python 3.12 is used inside a virtual environment for compatibility and stability with the libraries used by the project.

---

# Project Structure

```text
banking-support-ai/
│
├── app.py
├── agents.py
├── workflow.py
├── database.py
├── tools.py
├── logger_config.py
├── evaluation.py
├── requirements.txt
├── .env
├── .gitignore
│
├── data/
│   └── banking_support.db
│
└── tests/
```

### File Descriptions

| File | Purpose |
|---|---|
| `app.py` | Streamlit user interface |
| `agents.py` | CrewAI agent and LLM definitions |
| `workflow.py` | Agent routing and application workflow |
| `database.py` | SQLite database operations |
| `tools.py` | Ticket generation and ticket extraction utilities |
| `logger_config.py` | Python application logging |
| `evaluation.py` | Classification test cases and evaluation |
| `requirements.txt` | Python project dependencies |
| `.env` | API keys and local environment configuration |

---

# Installation

## 1. Clone the Repository

```bash
git clone <your-github-repository-url>
```

Move into the project directory:

```bash
cd banking-support-ai
```

---

## 2. Install Python

This project was tested using:

```text
Python 3.12
```

Verify your Python installation:

```bash
python3.12 --version
```

---

## 3. Create a Virtual Environment

Create the environment:

```bash
python3.12 -m venv .venv
```

Activate it on Linux:

```bash
source .venv/bin/activate
```

Your terminal should now show something similar to:

```text
(.venv) user@computer:~/banking-support-ai$
```

Confirm the Python version:

```bash
python --version
```

---

## 4. Upgrade pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

---

## 5. Install Project Dependencies

Install using:

```bash
python -m pip install -r requirements.txt
```

If CrewAI requires LiteLLM support, install:

```bash
python -m pip install "crewai[litellm]"
```

The main dependencies include:

```text
crewai
litellm
groq
streamlit
python-dotenv
pandas
```

---

# Groq API Configuration

This project uses **Groq** as the LLM provider.

Create a Groq API key and add it to a local `.env` file.

Create:

```text
.env
```

Add:

```env
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=groq/openai/gpt-oss-20b
```

Do not place quotation marks around the API key.

Example:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=groq/openai/gpt-oss-20b
```

---

# Important Security Note

Never upload the `.env` file or your API key to GitHub.

Make sure `.gitignore` contains:

```text
.env
.venv/
__pycache__/
*.pyc
banking_support.log
```

The SQLite database may also be ignored if you do not want customer test data uploaded:

```text
data/
*.db
```

---

# SQLite Installation on Fedora

Python includes SQLite support through the built-in `sqlite3` module.

For command-line SQLite and the graphical database browser on Fedora:

```bash
sudo dnf install sqlite sqlitebrowser
```

Check the SQLite installation:

```bash
sqlite3 --version
```

Launch DB Browser for SQLite:

```bash
sqlitebrowser
```

The application automatically creates the database at:

```text
data/banking_support.db
```

You can open this file using DB Browser for SQLite.

---

# Database Tables

## support_tickets

Stores support tickets generated for negative customer feedback.

Important fields include:

```text
ticket_number
customer_name
message
status
created_at
updated_at
```

Possible statuses include:

```text
Unresolved
In Progress
Resolved
```

## interaction_logs

Stores agent activity and customer interactions.

Fields include:

```text
customer_name
user_message
classification
agent_used
response
ticket_number
action
success
created_at
```

---

# Running the Application

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Start Streamlit:

```bash
python -m streamlit run app.py
```

The terminal should display something similar to:

```text
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

Open the Local URL in a browser.

---

# Stopping the Application

In the terminal where Streamlit is running, press:

```text
Ctrl + C
```

Closing the browser window alone does not necessarily stop the Streamlit server.

---

# Streamlit Dashboard

The application contains four main tabs.

## Customer Support

Allows a customer message to be submitted to the multi-agent workflow.

The application displays:

```text
Classification
Agent Route
AI Response
Database Interaction
Ticket Number
```

---

## Tickets

Displays the SQLite support-ticket database.

Users can also change ticket status between:

```text
Unresolved
In Progress
Resolved
```

---

## Logs

Displays previous AI interactions and provides operational statistics including:

```text
Total Interactions
Successful Interactions
Failed Interactions
Success Rate
```

---

## Evaluation

Runs predefined classification test cases and displays:

```text
Test Cases
Passed
Failed
Classification Accuracy
```

---

# Sample Test Scenarios

## Positive Feedback

Customer:

```text
Thanks for resolving my credit card issue.
```

Expected route:

```text
Classifier Agent
      |
      v
POSITIVE_FEEDBACK
      |
      v
Feedback Handler Agent
```

---

## Negative Feedback

Customer:

```text
My debit card replacement still hasn't arrived.
```

Expected route:

```text
Classifier Agent
      |
      v
NEGATIVE_FEEDBACK
      |
      v
Feedback Handler Agent
      |
      v
Create Support Ticket
```

A unique six-digit ticket should be generated.

---

## Ticket Query

After creating a ticket, enter:

```text
Could you check the status of ticket 483921?
```

Expected route:

```text
Classifier Agent
      |
      v
QUERY
      |
      v
Query Handler Agent
      |
      v
SQLite Ticket Lookup
```

Example response:

```text
Your ticket #483921 is currently marked as: Unresolved.
```

---

# CrewAI and Groq Compatibility

During development, a compatibility issue was encountered in which CrewAI added a `cache_breakpoint` property to LLM messages that was not supported by the Groq API.

A compatibility workaround is included in `agents.py` before the CrewAI agents are initialized.

This allows CrewAI to communicate successfully with the selected Groq model through LiteLLM.

---

# Current Capabilities

The current system can:

- Classify banking customer messages
- Identify positive feedback
- Identify negative feedback
- Detect support-ticket queries
- Route messages to appropriate agents
- Generate personalized customer responses
- Generate unique six-digit support tickets
- Store tickets in SQLite
- Retrieve existing ticket status
- Update ticket status
- Log customer interactions
- Track agent success/failure
- Run classifier evaluation tests
- Calculate classification accuracy
- Display all functionality through Streamlit

---

# Future Improvements

Potential future enhancements include:

- LLM-based empathy scoring
- Response clarity scoring
- Professionalism scoring
- Automated routing accuracy measurement
- Customer satisfaction ratings
- Authentication
- Role-based access control
- Real banking API integration
- Cloud database integration
- Retrieval-Augmented Generation (RAG)
- Additional banking-specialist agents
- More advanced prompt tracing
- Production monitoring and observability

---

# Disclaimer

This application is an educational capstone project and is intended to demonstrate multi-agent Generative AI architecture.

It does not connect to real banking accounts, customer financial information, or production banking systems.

All customer names, messages, ticket numbers, and support records used during testing should be considered simulated data.
