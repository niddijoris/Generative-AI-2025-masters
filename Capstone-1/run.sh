#!/bin/bash
# Run script to ensure virtual environment is used

# Activate virtual environment and run streamlit
source .venv/bin/activate
.venv/bin/streamlit run app.py
