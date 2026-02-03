import streamlit as st
import os
from langchain_core.messages import AIMessage, HumanMessage
from agent import create_agent, create_github_issue
from dotenv import load_dotenv
from ingest import main as run_ingestion

load_dotenv()

st.set_page_config(page_title="Customer Support AI", page_icon="🤖")

@st.cache_resource
def automated_ingestion():
    run_ingestion()

# Run ingestion automatically on startup (cached)
with st.spinner("Updating knowledge base..."):
    automated_ingestion()

st.title("🤖 TechFlow Support Agent")

# Initialize session state for chat history and other flags
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "agent" not in st.session_state:
    st.session_state.agent = create_agent()

if "show_ticket_form" not in st.session_state:
    st.session_state.show_ticket_form = False

# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# Logic to handle ticket creation form
def submit_ticket():
    summary = st.session_state.ticket_summary
    desc = st.session_state.ticket_desc
    email = st.session_state.ticket_email
    name = st.session_state.ticket_name
    
    if summary and desc and email and name:
        with st.spinner("Creating ticket..."):
            result = create_github_issue(summary, desc, email, name)
            st.success(result)
            st.session_state.show_ticket_form = False
            # Add system message about ticket creation
            st.session_state.chat_history.append(AIMessage(content=f"Ticket created: {summary}"))
    else:
        st.error("Please fill all fields.")

# React to user input
if prompt := st.chat_input("How can I help you today?"):
    # Reset ticket form state on new query
    st.session_state.show_ticket_form = False
    
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(HumanMessage(content=prompt))

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent.invoke({
                    "input": prompt,
                    "chat_history": st.session_state.chat_history
                })
                
                output_text = response["output"]
                st.markdown(output_text)
                st.session_state.chat_history.append(AIMessage(content=output_text))
                
                # Check if we should show ticket button
                if "could not find the answer" in output_text.lower() or "not found" in output_text.lower():
                    st.session_state.show_ticket_form = True
                    st.rerun()
                    
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_history.append(AIMessage(content=error_msg))

# Dedicated section for ticket creation if flag is set
if st.session_state.show_ticket_form:
    st.divider()
    st.warning("I couldn't find an answer. Would you like to raise a support ticket?")
    with st.form("ticket_form"):
        st.text_input("Name", key="ticket_name")
        st.text_input("Email", key="ticket_email")
        st.text_input("Issue Summary", key="ticket_summary")
        st.text_area("Description", key="ticket_desc")
        st.form_submit_button("Create Ticket", on_click=submit_ticket)
