import os
from dotenv import load_dotenv
from agent import create_github_issue

load_dotenv()

def test_ticket_creation():
    print("Testing TicketSystem...")
    
    # Check env vars
    if not os.getenv("GITHUB_TOKEN"):
        print("Error: GITHUB_TOKEN not set in .env")
        return
        
    summary = "Test Ticket from Script"
    description = "This is a test ticket to verify the TicketSystem class."
    email = "test@example.com"
    name = "Test User"
    
    print(f"Creating ticket for project: {os.getenv('PROJECT_FOLDER', 'Default')}")
    result = create_github_issue(summary, description, email, name)
    print(result)

if __name__ == "__main__":
    test_ticket_creation()
