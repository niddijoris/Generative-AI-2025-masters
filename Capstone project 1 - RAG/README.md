# TechFlow Customer Support Agent 🤖

A robust, RAG-based AI agent designed to assist users by answering questions from local PDF documentation and seamlessly creating GitHub support tickets when answers are unavailable.

## 🌟 Features

*   **RAG (Retrieval-Augmented Generation)**: Answers user queries using a local knowledge base created from PDF documents.
*   **Smart Search & Synthesis**:
    *   **Typo Tolerance**: Handles misspellings (e.g., "solutiun") and infers user intent.
    *   **Relevance Filtering**: Automatically discards search results with a similarity score below **0.7** to prevent hallucinated answers from irrelevant text.
    *   **Comprehensive Summarization**: Synthesizes answers from multiple document chunks.
*   **Strict Citations**: Every answer includes mandatory source citations with filenames and page numbers (e.g., `**Source:** manual.pdf (Page 12)`).
*   **Automated Ticket System**:
    *   **Condition-Based**: Offers to create a ticket only when the agent explicitly "could not find the answer".
    *   **GitHub Integration**: Directly creates issues in a specified GitHub repository.
    *   **Project Organization**: Automatically applies labels and prefixes titles based on the configured `PROJECT_FOLDER`.
*   **Auto-Ingestion**: Automatically checks and updates the vector database from the `data/` directory when the application starts.

## 🛠️ Prerequisites

*   Python 3.9+
*   OpenAI API Key
*   GitHub Personal Access Token (with `repo` scope)

## 🚀 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd <project-directory>
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory (copy from `.env.example`):
    ```bash
    cp .env.example .env
    ```
    
    Update `.env` with your credentials:
    ```env
    OPENAI_API_KEY=sk-...
    GITHUB_TOKEN=ghp_...
    REPO_NAME=your_username/your_repo_name
    PROJECT_FOLDER=Capstone Project 1 - RAG  # Used for ticket labels/titles
    ```

4.  **Add Knowledge Base**
    Place your PDF documents into the `data/` folder.
    *   The system will automatically ingest them when you run the app.

## 💻 Usage

Start the Streamlit application:

```bash
streamlit run app.py
```

### How it works:
1.  **Ask a Question**: Type your query in the chat.
2.  **Get an Answer**: The agent searches the PDFs. 
    *   If a high-confidence answer is found (Score > 0.7), it answers with citations.
    *   If relevant info is NOT found, it replies "I could not find the answer".
3.  **Raise a Ticket**: If the answer was not found, a form appears allowing you to create a GitHub issue immediately.

## 🧪 Testing & Verification

*   **Test Ticket Creation**: Run the dedicated test script to verify GitHub connectivity:
    ```bash
    python test_ticket.py
    ```
*   **Verify Ingestion**: Check the terminal output when starting the app to see "Creating vector database..." logs.

## 📁 Project Structure

*   `app.py`: Main Streamlit application entry point.
*   `agent.py`: Core logic for the AI agent, RAG search, and TicketSystem.
*   `ingest.py`: Script handles loading PDFs, chunking, and FAISS vector storage.
*   `data/`: Directory for source PDF files.
*   `vector_db/`: Directory where the FAISS index is saved locally.
