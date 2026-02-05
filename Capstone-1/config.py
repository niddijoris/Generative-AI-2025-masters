"""
Configuration management for Data Insights App
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4-turbo-preview"  # Model with function calling support

# GitHub Configuration (Optional)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
GITHUB_FOLDER = os.getenv("GITHUB_FOLDER", "")  # Optional folder/project prefix for issues

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATABASE_DIR / "car_prices.db"))
CSV_DATA_PATH = DATA_DIR / "car_prices.csv"

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_LOG_ENTRIES = 100  # Maximum number of log entries to keep in sidebar

# Sample queries for user guidance
SAMPLE_QUERIES = [
    "What's the average selling price of BMW cars?",
    "Show me the top 5 most expensive car models",
    "How many cars were sold in California?",
    "What's the price difference between automatic and manual transmission?",
    "Show statistics about cars in excellent condition",
    "Which seller has the most cars in the database?",
]

# Safety settings
ALLOWED_SQL_OPERATIONS = ["SELECT"]
DANGEROUS_SQL_KEYWORDS = [
    "DELETE", "DROP", "TRUNCATE", "ALTER", 
    "UPDATE", "INSERT", "CREATE", "REPLACE"
]
