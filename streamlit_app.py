"""
Streamlit Chatbot Interface
Modern web-based chat interface for the intelligent NL2SQL system
"""
import streamlit as st
import os
from setup_database import get_database_connection, download_chinook_database
from agent import IntelligentAgent


# Page configuration
st.set_page_config(
    page_title="Talk to Your Data - Intelligent NL2SQL",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        background-color: #262730;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sql-code {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #00d4ff;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
    }
    .reasoning-trace {
        background-color: #2b2d42;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff006e;
        font-family: 'JetBrains Mono', monospace;
        white-space: pre-wrap;
        font-size: 0.85em;
        color: #e0e0e0;
    }
    h1 {
        background: linear-gradient(45deg, #00d4ff, #ff006e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00d4ff, #0096c7);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_agent(api_key: str):
    """Initialize the database connection and agent (cached)"""
    # Download database if needed
    download_chinook_database("chinook.db")
    
    # Create connection and agent
    conn = get_database_connection("chinook.db")
    agent = IntelligentAgent(conn, api_key)
    
    return agent


def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "show_sql" not in st.session_state:
        st.session_state.show_sql = True
    if "show_reasoning" not in st.session_state:
        st.session_state.show_reasoning = False


def main():
    """Main application"""
    
    # Initialize
    init_session_state()
    
    # Header
    st.title("💬 Talk to Your Data")
    st.markdown("### Intelligent Natural Language to SQL System")
    st.markdown("Ask questions about the Chinook music database in plain English!")
    
    # Sidebar
    with st.sidebar:
        st.header("🔑 API Key")
        
        # API Key input
        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            value=os.getenv('GOOGLE_API_KEY', ''),
            help="Get your free API key from: https://aistudio.google.com/app/apikey"
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your API key above to start chatting!")
            st.stop()
        
        # Aggressively clean the key (prevent gRPC metadata errors)
        api_key = api_key.strip().replace('\r', '').replace('\n', '')
        
        st.divider()
        
        st.header("⚙️ Settings")
        
        # Toggle options
        st.session_state.show_sql = st.checkbox(
            "Show SQL Queries",
            value=st.session_state.show_sql
        )
        st.session_state.show_reasoning = st.checkbox(
            "Show Reasoning Trace",
            value=st.session_state.show_reasoning
        )
        
        st.divider()
        
        # Example questions
        st.header("💡 Example Questions")
        
        examples = {
            "Simple": [
                "How many customers are from Brazil?",
                "List all albums by AC/DC"
            ],
            "Moderate": [
                "Which 5 artists have the most tracks?",
                "Total revenue by country"
            ],
            "Complex": [
                "Customers who bought both Rock and Jazz",
                "Which artist has tracks in the most playlists?"
            ],
            "Meta": [
                "What tables exist?",
                "Show schema of Invoice table"
            ]
        }
        
        for category, questions in examples.items():
            with st.expander(f"**{category}**"):
                for q in questions:
                    if st.button(q, key=f"example_{q}"):
                        st.session_state.user_question = q
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Info
        st.markdown("---")
        st.markdown("**About**")
        st.caption("This system uses multi-step reasoning, schema exploration, and error recovery to generate accurate SQL queries from natural language.")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show SQL if available
            if message.get("sql") and st.session_state.show_sql:
                with st.expander("🔍 Generated SQL", expanded=False):
                    st.code(message["sql"], language="sql")
            
            # Show reasoning if available
            if message.get("reasoning") and st.session_state.show_reasoning:
                with st.expander("🧠 Reasoning Trace", expanded=False):
                    st.text(message["reasoning"])
    
    # Chat input
    user_input = st.chat_input("Ask a question about the database...")
    
    # Handle example button clicks
    if "user_question" in st.session_state:
        user_input = st.session_state.user_question
        del st.session_state.user_question
    
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Add to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Initialize agent with API key from sidebar
                    agent = initialize_agent(api_key)
                    
                    # Get response
                    result = agent.answer_question(user_input)
                    
                    # Display answer
                    if result.get('success') or result.get('is_meta'):
                        st.markdown(result['answer'])
                        
                        # Store in history
                        message_data = {
                            "role": "assistant",
                            "content": result['answer'],
                            "sql": result.get('sql'),
                            "reasoning": result.get('reasoning_steps') or result.get('reasoning')
                        }
                        st.session_state.messages.append(message_data)
                        
                        # Show SQL
                        if result.get('sql') and st.session_state.show_sql:
                            with st.expander("🔍 Generated SQL", expanded=False):
                                st.code(result['sql'], language="sql")
                        
                        # Show reasoning
                        if result.get('reasoning_steps') and st.session_state.show_reasoning:
                            with st.expander("🧠 Reasoning Trace", expanded=False):
                                st.text(result['reasoning_steps'])
                        
                        # Show metadata
                        if result.get('success') and not result.get('is_meta'):
                            st.caption(f"⏱️ Execution time: {result.get('execution_time', 0):.3f}s | Rows: {result.get('row_count', 0)}")
                    
                    else:
                        # Error case
                        st.error(result.get('answer', 'An error occurred'))
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"❌ {result.get('answer', 'An error occurred')}"
                        })
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ Error: {str(e)}"
                    })


if __name__ == "__main__":
    main()
