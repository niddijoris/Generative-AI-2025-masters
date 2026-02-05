"""
SQL Safety Validator - Prevents dangerous database operations
"""
import re
from typing import Tuple
from config import ALLOWED_SQL_OPERATIONS, DANGEROUS_SQL_KEYWORDS


class SafetyValidator:
    """Validates SQL queries to prevent dangerous operations"""
    
    @staticmethod
    def validate_query(query: str) -> Tuple[bool, str]:
        """
        Validate if a SQL query is safe to execute
        
        Args:
            query: SQL query string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if query is safe, False otherwise
            - error_message: Empty string if valid, error description if invalid
        """
        if not query or not query.strip():
            return False, "Empty query provided"
        
        # Normalize query for checking
        normalized_query = query.strip().upper()
        
        # Check for dangerous keywords
        for keyword in DANGEROUS_SQL_KEYWORDS:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, normalized_query):
                return False, (
                    f"🚫 BLOCKED: Query contains dangerous operation '{keyword}'. "
                    f"Only SELECT queries are allowed for safety reasons."
                )
        
        # Ensure query starts with SELECT
        if not normalized_query.startswith('SELECT'):
            return False, (
                "🚫 BLOCKED: Only SELECT queries are allowed. "
                "This application is read-only to prevent accidental data modification."
            )
        
        # Additional checks for SQL injection patterns
        suspicious_patterns = [
            r';.*?(DELETE|DROP|UPDATE|INSERT)',  # Multiple statements
            r'--',  # SQL comments (potential injection)
            r'/\*.*?\*/',  # Block comments
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, normalized_query, re.IGNORECASE | re.DOTALL):
                return False, (
                    "🚫 BLOCKED: Query contains suspicious patterns that may indicate "
                    "SQL injection or multiple statements. Please use simple SELECT queries."
                )
        
        return True, ""
    
    @staticmethod
    def get_safety_message() -> str:
        """Get a message explaining safety restrictions"""
        return (
            "🛡️ **Safety Features Active**\n\n"
            f"✅ Allowed operations: {', '.join(ALLOWED_SQL_OPERATIONS)}\n"
            f"❌ Blocked operations: {', '.join(DANGEROUS_SQL_KEYWORDS)}\n\n"
            "This ensures your data remains safe from accidental modifications."
        )
