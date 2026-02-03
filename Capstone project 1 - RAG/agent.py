import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from github import Github
from github import Auth

load_dotenv()

# Constants / Config
COMPANY_NAME = "TechFlow Solutions"
COMPANY_CONTACT = "support@techflow.com | +1-555-0199"
DB_PATH = "vector_db"

def get_vector_store():
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.load_local(
        DB_PATH, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    return vector_store

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the company knowledge base for answers to user questions.
    Returns relevance of text and citations (source files and page numbers).
    """
    try:
        vector_store = get_vector_store()
        # Use relevance scores (0 to 1, where 1 is best match)
        results = vector_store.similarity_search_with_relevance_scores(query, k=5)
        
        response = ""
        relevant_count = 0
        
        # Threshold for relevance (0.7 is a reasonable baseline for OpenAI embeddings)
        THRESHOLD = 0.7
        
        print(f"\n--- Search Query: '{query}' ---")
        for i, (doc, score) in enumerate(results):
            print(f"Result {i+1}: Score {score:.4f} | Content: {doc.page_content[:50]}...")
            
            if score < THRESHOLD:
                print(f"  -> FILTERED (Below {THRESHOLD})")
                continue
                
            relevant_count += 1
            print(f"  -> ACCEPTED")
            if score < THRESHOLD:
                continue
                
            relevant_count += 1
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "Unknown")
            # Extract just the filename from the path
            filename = os.path.basename(source)
            
            response += f"--- Result {relevant_count} (Score: {score:.2f}) ---\n"
            response += f"Content: {doc.page_content}\n"
            response += f"Source: {filename}, Page: {page}\n\n"
            
        return response if response else "No relevant information found in the knowledge base (all results below threshold)."
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"

class TicketSystem:
    def __init__(self, token, repo_name):
        auth = Auth.Token(token)
        self.g = Github(auth=auth)
        self.repo = self.g.get_repo(repo_name)

    def create_ticket(self, title, body, project_folder):
        """
        project_folder: Project folder name (e.g. 'Capstone2-1.2Antigravity')
        """
        # 1. Check or create label
        label_name = project_folder.lower().replace("/", "-").replace(" ", "-")
        try:
            self.repo.get_label(label_name)
        except:
            # Create new label (blue)
            self.repo.create_label(name=label_name, color="0075ca")

        # 2. Decorate title
        full_title = f"[{project_folder}] {title}"
        
        # 3. Add details to body
        full_body = f"**Project:** {project_folder}\n\n**Description:**\n{body}"

        # 4. Create Issue
        new_issue = self.repo.create_issue(
            title=full_title,
            body=full_body,
            labels=[label_name, "customer-support"]
        )
        return new_issue

def create_github_issue(summary: str, description: str, user_email: str, user_name: str) -> str:
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("REPO_NAME")
    project_folder = os.getenv("PROJECT_FOLDER", "Capstone Project")
    
    if not token or not repo_name:
        return "Error: GitHub credentials not configured. Cannot create ticket."

    try:
        ticket_system = TicketSystem(token, repo_name)
        
        # Combine user details into the body description
        full_description = f"**User Name:** {user_name}\n**User Email:** {user_email}\n\n{description}"
        
        issue = ticket_system.create_ticket(
            title=summary,
            body=full_description,
            project_folder=project_folder
        )
        
        return f"Ticket created successfully! Ticket ID: #{issue.number}. Link: {issue.html_url}"
    except Exception as e:
        return f"Error creating ticket: {str(e)}"

@tool
def create_support_ticket(summary: str, description: str, user_email: str, user_name: str) -> str:
    """
    Create a support ticket (GitHub Issue) for the user.
    Use this when the knowledge base doesn't have the answer or the user explicitly asks to raise a ticket.
    Include all details: user name, email, issue summary and full description.
    """
    return create_github_issue(summary, description, user_email, user_name)

def create_agent():
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    tools = [search_knowledge_base, create_support_ticket]
    
    system_prompt = f"""You are a helpful and professional customer support agent for {COMPANY_NAME}.
    
    Company Contact Info: {COMPANY_CONTACT}
    
    Your goal is to assist users with their questions using the available tools.
    
    GUIDELINES:
    1.  **ALWAYS SEARCH**: You MUST use the `search_knowledge_base` tool for **EVERY** user message, even if it looks like a typo, gibberish, or nonsense. 
        - **Reason**: The search tool has internal logic to handle/reject irrelevant queries. You must let it run.
        - **Do not** simply reply "It seems like a typo" without calling the tool first.
    2.  **Intent**: If you can infer a valid term (e.g. "solutiun" -> "Solution"), search for the corrected term. If it is total gibberish, search for the gibberish exactly.
    2.  **Comprehensive Synthesis**: Use the provided search results to answer the user's question. 
        - **Summarize ALL chunks**: You must synthesize information from ALL relevant chunks provided by the search tool.
        - **Proactive Answering**: If exact matches aren't found, define related concepts (e.g., Software Architecture for Solution Architecture) found in the text.
        - **NEVER** refuse to answer if there is ANY retrieved text that is even remotely technical or relevant.
    3.  **MANDATORY CITATIONS**: You MUST list **ALL** source citations found in the search results at the end of your response.
        - Even if you summarize multiple chunks, list every unique source/page used.
        - Format: `**Source 1:** [filename] (Page [number])`
    4.  **IF ANSWER NOT FOUND**: Only if the search results are completely empty or nonsensical string matches, state: "I could not find the answer in the knowledge base." 
    5.  **Ticket Creation**: If you truly cannot help, or if the user explicitly asks, create a support ticket using `create_support_ticket`.
    6.  Required details for a ticket: Title (Summary), Description, User Name, User Email.
    7.  Be polite and concise.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent_executor
