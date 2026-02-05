"""
Utility functions for logging in Streamlit
"""
import logging
from datetime import datetime
from typing import List, Dict
import streamlit as st


class StreamlitLogHandler(logging.Handler):
    """Custom logging handler that stores logs in Streamlit session state"""
    
    def __init__(self, max_entries: int = 100):
        super().__init__()
        self.max_entries = max_entries
        
        # Initialize session state for logs if not exists
        if 'console_logs' not in st.session_state:
            st.session_state.console_logs = []
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record to session state"""
        try:
            log_entry = {
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'level': record.levelname,
                'message': self.format(record),
                'logger': record.name
            }
            
            # Add to session state
            st.session_state.console_logs.append(log_entry)
            
            # Keep only last N entries
            if len(st.session_state.console_logs) > self.max_entries:
                st.session_state.console_logs = st.session_state.console_logs[-self.max_entries:]
                
        except Exception:
            self.handleError(record)


def setup_logging(level: str = "INFO", max_entries: int = 100):
    """
    Set up logging with Streamlit handler
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        max_entries: Maximum number of log entries to keep
    """
    # Create streamlit handler
    streamlit_handler = StreamlitLogHandler(max_entries=max_entries)
    streamlit_handler.setLevel(getattr(logging, level))
    
    # Create formatter
    formatter = logging.Formatter('%(name)s - %(message)s')
    streamlit_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    
    # Remove existing handlers and add streamlit handler
    root_logger.handlers = []
    root_logger.addHandler(streamlit_handler)
    
    # Also add console handler for debugging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def get_logs() -> List[Dict]:
    """Get all logs from session state"""
    return st.session_state.get('console_logs', [])


def clear_logs():
    """Clear all logs from session state"""
    st.session_state.console_logs = []


def add_log(level: str, message: str, logger_name: str = "app"):
    """
    Manually add a log entry
    
    Args:
        level: Log level (INFO, WARNING, ERROR, DEBUG)
        message: Log message
        logger_name: Name of the logger
    """
    logger = logging.getLogger(logger_name)
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message)
