# 🚗 Data Insights App

An AI-powered data analysis platform that allows users to explore a massive car auction dataset (558,000+ records) using natural language. The app combines **Streamlit** for the interface, **SQLite** for data management, and **OpenAI's GPT-4** for intelligent analysis and dynamic chart generation.

---
[## Hugging Face](https://huggingface.co/spaces/niddijoris/ChatWithData)

## � Application Gallery

| Dashboard Overview | AI Chat & Analytics |
| :---: | :---: |
| ![Dashboard Overview](/screenshots/1.png) | ![AI Chat & Analytics](/screenshots/2.png) |
| **Real-time Statistics & Insights** | **Intelligent Querying & Data Analysis** |

| Dynamic Chart Generation | Safety & Logs |
| :---: | :---: |
| ![Chart Generation](/screenshots/3.png) | ![Console Logs](/screenshots/4.png) |
| **AI-driven Visualizations** | **Security Guardrails & Activity Monitoring** |

---

## 🌟 Key Features

### 🤖 Intelligent AI Agent
- **Natural Language Querying**: Ask questions like "What is the average price of a BMW?" or "Compare prices between California and Florida".
- **Dynamic Chart Generation**: Ask for visualizations (bar, line, pie, scatter) and the AI will generate them instantly.
- **Context-Aware Support**: If the agent can't help, it offers to create a GitHub support ticket with the chat history.

### 🛡️ Secure Data Management
- **ReadOnly Safety**: Strict SQL validation ensures only `SELECT` queries are executed. Dangerous operations (`DELETE`, `DROP`, `UPDATE`) are automatically blocked.
- **Privacy Guardrails**: The agent never communicates the full dataset, only relevant snippets (limited to 100 rows).

### 📊 Business Intelligence
- **Real-time Stats**: Instantly see total inventory, average prices, and price/year ranges in the sidebar.
- **Automated Insights**: Interactive top-make comparisons and condition distribution charts.
- **Console Monitoring**: A live developer console in the sidebar shows every action the AI and database are taking.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- OpenAI API Key

### 2. Setup
```bash
# Clone the repository and enter directory
cd "Capstone folder"

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```
**Required**: `OPENAI_API_KEY`  
**Optional**: `GITHUB_TOKEN` and `GITHUB_REPO` (for support tickets)

### 4. Run the Application
Use the automated run script to ensure the correct environment is used:
```bash
chmod +x run.sh
./run.sh
```

---

## �️ Project Architecture
- **`app.py`**: Main Streamlit interface.
- **`agent/`**: AI logic and tool definitions.
- **`database/`**: Safe SQL execution and CSV-to-SQLite ingestion.
- **`support/`**: GitHub API integration for support tickets.
- **`ui/`**: Chart generation (Plotly) and styling.
- **`utils/`**: Custom Streamlit-integrated logger.

---

## 🛡️ Security Policy
This application is designed with safety as a priority. The `SafetyValidator` provides a robust whitelist of allowed SQL operations, specifically protecting against SQL injection and unauthorized data modification.

🛡️ **Active Protections**: Only SELECT | All dangerous keywords blocked | Data remains secure
