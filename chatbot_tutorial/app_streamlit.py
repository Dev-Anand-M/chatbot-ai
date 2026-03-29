"""
Streamlit GUI for Chatbot
==========================

STEP 3: Building the User Interface
------------------------------------

WHY STREAMLIT?
- Most popular for Python chatbots
- Minimal code for full GUI
- Built-in chat interface
- Auto-reload during development
- Easy deployment

STREAMLIT BASICS:
- Runs top-to-bottom on every interaction
- Uses session_state for persistence
- Automatic UI rendering
- No HTML/CSS needed

CONVENTIONAL STRUCTURE:
1. Page configuration
2. Session state initialization
3. Sidebar (settings)
4. Main chat interface
5. Input handling
"""

import streamlit as st
from chatbot_core import ChatbotCore
from config import Config


# ============================================================================
# STEP 3.1: Page Configuration
# ============================================================================
# CONVENTION: Always configure page first, before any other st. calls

st.set_page_config(
    page_title=Config.APP_TITLE,      # Browser tab title
    page_icon=Config.APP_ICON,        # Browser tab icon
    layout="wide",                     # "wide" or "centered"
    initial_sidebar_state="expanded"   # Sidebar visible by default
)


# ============================================================================
# STEP 3.2: Session State Initialization
# ============================================================================
# SESSION STATE: Persists data across reruns
# CONVENTION: Initialize all state variables at the start

def initialize_session_state():
    """
    Initialize session state variables
    
    WHY NEEDED?
    - Streamlit reruns script on every interaction
    - Session state preserves data between reruns
    - Prevents re-initialization
    
    PATTERN: Check if exists, then initialize
    """
    
    # Chatbot instance
    # IMPORTANT: Only create once, reuse across reruns
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = ChatbotCore(provider="openai")
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            st.stop()  # Stop execution if initialization fails
    
    # Chat messages for display
    # STRUCTURE: List of {"role": "user/assistant", "content": "text"}
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # UI state flags
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False


# Initialize on app start
initialize_session_state()


# ============================================================================
# STEP 3.3: Sidebar - Settings and Controls
# ============================================================================
# SIDEBAR: Common pattern for chatbot settings
# CONVENTION: Settings, info, and actions in sidebar

with st.sidebar:
    st.header("⚙️ Settings")
    
    # Display current configuration
    # PATTERN: Show user what settings are active
    st.info(f"""
    **Model:** {Config.MODEL_NAME}  
    **Temperature:** {Config.TEMPERATURE}  
    **Max History:** {Config.MAX_HISTORY} messages
    """)
    
    # Conversation statistics
    # PATTERN: Give user feedback about conversation state
    st.metric(
        label="Messages",
        value=st.session_state.chatbot.get_message_count()
    )
    
    st.divider()  # Visual separator
    
    # Clear conversation button
    # CONVENTION: Destructive actions need confirmation
    st.subheader("🗑️ Actions")
    
    if st.button("Clear Conversation", type="primary", use_container_width=True):
        # Reset chatbot
        st.session_state.chatbot.reset_conversation()
        # Clear display messages
        st.session_state.messages = []
        # Force rerun to update UI
        st.rerun()
    
    st.divider()
    
    # Help section
    # PATTERN: Provide user guidance
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        1. Type your message in the input box
        2. Press Enter or click Send
        3. Wait for AI response
        4. Continue conversation
        5. Click "Clear" to start over
        """)
    
    # Debug info (optional)
    # PATTERN: Show technical details for developers
    with st.expander("🔧 Debug Info"):
        st.json({
            "provider": st.session_state.chatbot.provider,
            "model": st.session_state.chatbot.model,
            "message_count": st.session_state.chatbot.get_message_count(),
            "history_length": len(st.session_state.chatbot.messages)
        })


# ============================================================================
# STEP 3.4: Main Chat Interface
# ============================================================================
# MAIN AREA: Chat display and input

# Title and description
st.title(f"{Config.APP_ICON} {Config.APP_TITLE}")
st.caption("Powered by OpenAI GPT • Built with Streamlit")

# Display chat messages
# PATTERN: Show conversation history
# CONVENTION: Use st.chat_message for proper formatting

for message in st.session_state.messages:
    """
    CHAT MESSAGE STRUCTURE:
    - role: "user" or "assistant"
    - content: message text
    
    st.chat_message() provides:
    - Proper avatar (user/assistant icon)
    - Message bubble styling
    - Consistent formatting
    """
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================================
# STEP 3.5: User Input Handling
# ============================================================================
# CHAT INPUT: Streamlit's built-in chat input widget
# CONVENTION: Place at bottom of chat interface

user_input = st.chat_input("Type your message here...")

if user_input:
    """
    INPUT FLOW:
    1. User types and presses Enter
    2. Display user message immediately
    3. Add to chatbot history
    4. Get AI response
    5. Display AI response
    6. Update session state
    
    WHY THIS ORDER?
    - Immediate feedback (user sees their message)
    - Progressive disclosure (show thinking state)
    - Error handling at each step
    """
    
    # Display user message immediately
    # PATTERN: Optimistic UI update
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Add to display history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Get AI response
    # PATTERN: Show loading state during API call
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):  # Loading indicator
            try:
                # Add message to chatbot
                st.session_state.chatbot.add_user_message(user_input)
                
                # Get response from AI
                response = st.session_state.chatbot.get_response()
                
                # Display response
                st.markdown(response)
                
                # Add to display history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
            except Exception as e:
                # ERROR HANDLING: Show user-friendly error
                error_message = f"❌ Error: {str(e)}"
                st.error(error_message)
                
                # Add error to display
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })


# ============================================================================
# STEP 3.6: Footer
# ============================================================================
# PATTERN: Add helpful information at bottom

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("💡 Tip: Be specific in your questions")

with col2:
    st.caption("⚡ Responses typically take 2-5 seconds")

with col3:
    st.caption("🔒 Your conversations are not stored")


# ============================================================================
# HOW TO RUN THIS APP
# ============================================================================
"""
COMMAND:
    streamlit run app_streamlit.py

WHAT HAPPENS:
1. Streamlit starts local web server
2. Opens browser automatically
3. Runs this script
4. Watches for file changes (auto-reload)

STREAMLIT FEATURES USED:
- st.set_page_config() - Page settings
- st.session_state - Data persistence
- st.sidebar - Side panel
- st.chat_message() - Chat bubbles
- st.chat_input() - Input widget
- st.spinner() - Loading indicator
- st.button() - Interactive button
- st.rerun() - Force refresh

CONVENTIONAL PATTERNS:
✅ Session state for persistence
✅ Sidebar for settings
✅ Chat messages for display
✅ Error handling with try-except
✅ Loading indicators for API calls
✅ Clear button for reset
✅ Help section for users
"""
