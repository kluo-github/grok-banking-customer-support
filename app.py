import pandas as pd
import streamlit as st

from database import (
    initialize_database,
    get_all_tickets,
    get_all_logs,
    update_ticket_status
)

from workflow import process_customer_message
from evaluation import evaluate_classifier


initialize_database()


st.set_page_config(
    page_title="Banking Customer Support AI",
    page_icon="🏦",
    layout="wide"
)


st.title("🏦 Banking Customer Support AI")

st.caption(
    "Multi-Agent Customer Support System using CrewAI, "
    "SQLite and Streamlit"
)


tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Customer Support",
    "🎫 Tickets",
    "📋 Logs",
    "📊 Evaluation"
])


# -----------------------------------------------------
# CUSTOMER SUPPORT TAB
# -----------------------------------------------------

with tab1:

    st.header("Customer Support Assistant")

    customer_name = st.text_input(
        "Customer Name",
        placeholder="Enter customer name"
    )

    message = st.text_area(
        "Customer Message",
        placeholder=(
            "Example: My debit card replacement still hasn't arrived."
        ),
        height=140
    )

    submit = st.button(
        "Submit Request",
        type="primary"
    )

    if submit:

        if not customer_name.strip():
            st.warning("Please enter a customer name.")

        elif not message.strip():
            st.warning("Please enter a customer message.")

        else:

            with st.spinner(
                "AI agents are processing the request..."
            ):

                try:

                    result = process_customer_message(
                        customer_name.strip(),
                        message.strip()
                    )

                    st.session_state["last_result"] = result

                except Exception as error:

                    st.error(
                        f"An error occurred: {error}"
                    )

    if "last_result" in st.session_state:

        result = st.session_state["last_result"]

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Classification")
            st.info(
                result["classification"]
            )

        with col2:
            st.subheader("Agent Route")
            st.info(
                f"Classifier Agent → {result['agent']}"
            )

        st.subheader("AI Response")

        if result["success"]:
            st.success(
                result["response"]
            )
        else:
            st.warning(
                result["response"]
            )

        st.subheader("Database Interaction")

        st.code(
            result["database_action"]
        )

        if result.get("ticket_number"):

            st.metric(
                "Ticket Number",
                result["ticket_number"]
            )


# -----------------------------------------------------
# TICKETS TAB
# -----------------------------------------------------

with tab2:

    st.header("Support Ticket Database")

    tickets = get_all_tickets()

    if tickets:

        tickets_df = pd.DataFrame(tickets)

        st.dataframe(
            tickets_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No support tickets have been created yet."
        )

    st.divider()

    st.subheader("Update Ticket Status")

    update_ticket = st.text_input(
        "Ticket Number",
        key="ticket_update_number"
    )

    new_status = st.selectbox(
        "New Status",
        [
            "Unresolved",
            "In Progress",
            "Resolved"
        ]
    )

    if st.button(
        "Update Ticket"
    ):

        if not update_ticket.strip():

            st.warning(
                "Please enter a ticket number."
            )

        else:

            success = update_ticket_status(
                update_ticket.strip(),
                new_status
            )

            if success:

                st.success(
                    f"Ticket #{update_ticket} "
                    f"updated to {new_status}."
                )

                st.rerun()

            else:

                st.error(
                    "Ticket number not found."
                )


# -----------------------------------------------------
# LOGS TAB
# -----------------------------------------------------

with tab3:

    st.header("Agent Logs and Debugging")

    logs = get_all_logs()

    if logs:

        logs_df = pd.DataFrame(logs)

        st.dataframe(
            logs_df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("System Metrics")

        total_interactions = len(logs_df)

        successful = int(
            logs_df["success"].sum()
        )

        failed = (
            total_interactions -
            successful
        )

        success_rate = (
            successful /
            total_interactions *
            100
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Interactions",
            total_interactions
        )

        col2.metric(
            "Successful",
            successful
        )

        col3.metric(
            "Failed",
            failed
        )

        col4.metric(
            "Success Rate",
            f"{success_rate:.1f}%"
        )

    else:

        st.info(
            "No interaction logs available yet."
        )


# -----------------------------------------------------
# EVALUATION TAB
# -----------------------------------------------------

with tab4:

    st.header("Model Evaluation")

    st.write(
        """
        This section evaluates the Classifier Agent using
        predefined banking customer support test cases.
        """
    )

    st.warning(
        "Running evaluation calls the LLM several times "
        "and may take a little time."
    )

    if st.button(
        "Run Classification Evaluation"
    ):

        with st.spinner(
            "Running evaluation test cases..."
        ):

            try:

                evaluation = evaluate_classifier()

                st.session_state[
                    "evaluation"
                ] = evaluation

            except Exception as error:

                st.error(
                    f"Evaluation failed: {error}"
                )

    if "evaluation" in st.session_state:

        evaluation = st.session_state[
            "evaluation"
        ]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Test Cases",
            evaluation["total"]
        )

        col2.metric(
            "Passed",
            evaluation["correct"]
        )

        col3.metric(
            "Failed",
            evaluation["incorrect"]
        )

        col4.metric(
            "Classification Accuracy",
            f"{evaluation['accuracy']}%"
        )

        st.subheader(
            "Test Case Results"
        )

        evaluation_df = pd.DataFrame(
            evaluation["results"]
        )

        st.dataframe(
            evaluation_df,
            use_container_width=True,
            hide_index=True
        )