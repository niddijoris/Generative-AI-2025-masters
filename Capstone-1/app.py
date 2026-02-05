"""
Data Insights App - Main Streamlit Application
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from config import OPENAI_API_KEY, SAMPLE_QUERIES, MAX_LOG_ENTRIES
from database import DatabaseManager
from agent import AIAgent, AgentTools
from support import GitHubSupport
from utils import setup_logging, get_logs, clear_logs
from ui import (
    create_price_distribution_chart,
    create_top_makes_chart,
    create_condition_pie_chart,
    create_price_by_make_chart,
    create_dynamic_chart
)


# Page configuration
st.set_page_config(
    page_title="Data Insights App",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    .log-entry {
        font-family: monospace;
        font-size: 0.85rem;
        padding: 0.3rem;
        margin: 0.2rem 0;
        border-left: 3px solid #ddd;
        padding-left: 0.5rem;
    }
    .log-info {
        border-left-color: #2ca02c;
    }
    .log-warning {
        border-left-color: #ff7f0e;
    }
    .log-error {
        border-left-color: #d62728;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'initialized' not in st.session_state:
        # Set up logging
        setup_logging(level="INFO", max_entries=MAX_LOG_ENTRIES)
        
        # Initialize database
        st.session_state.db_manager = DatabaseManager()
        
        # Initialize GitHub support
        st.session_state.github_support = GitHubSupport()
        
        # Initialize agent tools and AI agent
        st.session_state.tools = AgentTools(
            db_manager=st.session_state.db_manager,
            github_support=st.session_state.github_support
        )
        st.session_state.agent = AIAgent(tools=st.session_state.tools)
        
        # Chat history
        st.session_state.messages = []
        
        # Statistics cache
        st.session_state.stats = None
        st.session_state.stats_loaded = False
        
        st.session_state.initialized = True


def load_statistics():
    """Load database statistics (cached)"""
    if not st.session_state.stats_loaded:
        st.session_state.stats = st.session_state.db_manager.get_statistics()
        st.session_state.stats_loaded = True
    return st.session_state.stats


def render_sidebar():
    """Render sidebar with logs, stats, and charts"""
    with st.sidebar:
        st.markdown("### 🎛️ Control Panel")
        
        # API Key check
        if not OPENAI_API_KEY:
            st.error("⚠️ OPENAI_API_KEY not set! Please configure your .env file.")
            st.stop()
        else:
            st.success("✅ OpenAI API Connected")
        
        st.divider()
        
        # Database Statistics
        st.markdown("### 📊 Database Overview")
        stats = load_statistics()
        
        if stats:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{stats.get('total_records', 0):,}</div>
                    <div class="stat-label">Total Cars</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_price = stats.get('avg_price', 0)
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">${avg_price:,.0f}</div>
                    <div class="stat-label">Avg Price</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Price range
            min_price = stats.get('min_price', 0)
            max_price = stats.get('max_price', 0)
            st.markdown(f"**Price Range:** ${min_price:,} - ${max_price:,}")
            
            # Year range
            year_range = stats.get('year_range', {})
            st.markdown(f"**Year Range:** {year_range.get('min', 'N/A')} - {year_range.get('max', 'N/A')}")
        
        st.divider()
        
        # Charts
        st.markdown("### 📈 Insights")
        
        if stats:
            # Top makes chart
            with st.expander("🏆 Top Makes", expanded=False):
                fig = create_top_makes_chart(stats)
                st.plotly_chart(fig, use_container_width=True)
            
            # Condition distribution
            with st.expander("🔍 Condition Distribution", expanded=False):
                fig = create_condition_pie_chart(stats)
                st.plotly_chart(fig, use_container_width=True)
            
            # Average price by make
            with st.expander("💰 Avg Price by Make", expanded=False):
                fig = create_price_by_make_chart(st.session_state.db_manager)
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Sample Queries
        st.markdown("### 💡 Sample Queries")
        for i, query in enumerate(SAMPLE_QUERIES[:4]):
            if st.button(f"📝 {query[:40]}...", key=f"sample_{i}", use_container_width=True):
                st.session_state.sample_query = query
                st.rerun()
        
        st.divider()
        
        # Console Logs
        st.markdown("### 🖥️ Console Logs")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                clear_logs()
                st.rerun()
        
        # Display logs
        logs = get_logs()
        
        if logs:
            log_container = st.container(height=300)
            with log_container:
                for log in reversed(logs[-50:]):  # Show last 50 logs
                    level = log['level'].lower()
                    css_class = f"log-{level}"
                    
                    st.markdown(f"""
                    <div class="log-entry {css_class}">
                        <strong>[{log['timestamp']}]</strong> {log['level']}: {log['message']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No logs yet. Start chatting to see activity!")


def render_chat_interface():
    """Render main chat interface"""
    # Header
    st.markdown('<div class="main-header">🚗 Car Data Insights Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask questions about car auction data powered by AI</div>', unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("chart"):
                chart_config = message["chart"]
                fig = create_dynamic_chart(
                    data=chart_config['data'],
                    chart_type=chart_config['type'],
                    title=chart_config['title'],
                    x_label=chart_config['x_label'],
                    y_label=chart_config['y_label']
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Handle sample query selection
    if 'sample_query' in st.session_state:
        user_input = st.session_state.sample_query
        del st.session_state.sample_query
    else:
        user_input = st.chat_input("Ask me anything about the car data...")
        # Process user input
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_data = st.session_state.agent.chat(user_input)
                content = response_data["content"]
                chart = response_data.get("chart")
                
                st.markdown(content)
                if chart:
                    fig = create_dynamic_chart(
                        data=chart['data'],
                        chart_type=chart['type'],
                        title=chart['title'],
                        x_label=chart['x_label'],
                        y_label=chart['y_label']
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Add assistant response to chat
        st.session_state.messages.append({
            "role": "assistant", 
            "content": content,
            "chart": chart
        })
        
        st.rerun()


def render_support_section():
    """Render support ticket creation section"""
    st.divider()
    
    with st.expander("🎫 Need Human Support?", expanded=False):
        st.markdown("""
        If the AI assistant can't help you, create a support ticket to reach a human expert.
        Your conversation history will be included automatically.
        """)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            ticket_title = st.text_input(
                "Issue Summary",
                placeholder="Brief description of your issue..."
            )
        
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"])
        
        ticket_description = st.text_area(
            "Details",
            placeholder="Provide more details about your issue...",
            height=100
        )
        
        if st.button("📤 Create Support Ticket", type="primary"):
            if not ticket_title:
                st.error("Please provide a ticket title")
            else:
                # Get conversation context
                context = st.session_state.agent.get_conversation_context()
                
                # Create full description with context
                full_description = f"{ticket_description}\n\n---\n\n**Conversation History:**\n\n{context}"
                
                # Create ticket
                result = st.session_state.tools.execute_tool(
                    "create_support_ticket",
                    {
                        "title": ticket_title,
                        "description": full_description,
                        "priority": priority
                    }
                )
                
                if result.get('success'):
                    st.success(f"✅ {result.get('message')}")
                    if 'issue_url' in result:
                        st.markdown(f"**Issue URL:** {result['issue_url']}")
                    elif 'ticket_id' in result:
                        st.markdown(f"**Ticket ID:** {result['ticket_id']}")
                else:
                    st.error(f"❌ {result.get('error')}")


def main():
    """Main application entry point"""
    # Initialize
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main chat interface
    render_chat_interface()
    
    # Render support section
    render_support_section()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        🛡️ <strong>Safety Features Active:</strong> Only SELECT queries allowed | 
        All dangerous operations blocked | 
        Data remains secure
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
