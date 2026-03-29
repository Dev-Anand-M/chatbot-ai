"""
Gradio GUI for Chatbot (Alternative to Streamlit)
==================================================

STEP 4: Alternative GUI Framework
----------------------------------

WHY GRADIO?
- Simpler than Streamlit for basic UIs
- Better for ML demos
- Automatic API generation
- Easy sharing (gradio.app hosting)
- Less code than Streamlit

GRADIO vs STREAMLIT:
- Gradio: Function-based, simpler
- Streamlit: Script-based, more features

WHEN TO USE GRADIO:
- Quick demos
- Simple interfaces
- ML model showcases
- Public sharing needed
"""

import gradio as gr
from chatbot_core import ChatbotCore
from config import Config


# ============================================================================
# STEP 4.1: Initialize Chatbot
# ============================================================================
# PATTERN: Global instance for Gradio
# WHY? Gradio uses function callbacks, needs accessible instance

try:
    chatbot = ChatbotCore(provider="openai")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    exit(1)


# ============================================================================
# STEP 4.2: Core Chat Function
# ============================================================================
# GRADIO PATTERN: Define function that processes input and returns output

def chat_function(message: str, history: list) -> str:
    """
    Process user message and return AI response
    
    Args:
        message: User's input text
        history: List of [user_msg, bot_msg] pairs
        
    Returns:
        AI's response text
        
    GRADIO CONVENTION:
    - Function receives current message + history
    - Returns only the response (Gradio handles display)
    - History is list of tuples: [(user1, bot1), (user2, bot2), ...]
    """
    
    if not message or not message.strip():
        return "Please enter a message."
    
    try:
        # Add user message to chatbot
        chatbot.add_user_message(message)
        
        # Get AI response
        response = chatbot.get_response()
        
        return response
        
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ============================================================================
# STEP 4.3: Clear Function
# ============================================================================
# PATTERN: Separate function for each action

def clear_conversation():
    """
    Reset conversation history
    
    Returns:
        None (clears the interface)
        
    GRADIO CONVENTION:
    - Return None to clear components
    - Or return new values to update them
    """
    chatbot.reset_conversation()
    return None  # Clears the chatbox


# ============================================================================
# STEP 4.4: Build Interface
# ============================================================================
# GRADIO BLOCKS: Modern API for custom layouts
# ALTERNATIVE: gr.Interface (simpler but less flexible)

with gr.Blocks(
    title=Config.APP_TITLE,
    theme=gr.themes.Soft()  # Built-in theme
) as demo:
    """
    GRADIO BLOCKS STRUCTURE:
    - with gr.Blocks() as demo: - Main container
    - gr.Markdown() - Static text
    - gr.Chatbot() - Chat display
    - gr.Textbox() - Input field
    - gr.Button() - Action button
    - .click() - Event handler
    """
    
    # Header
    gr.Markdown(f"""
    # {Config.APP_ICON} {Config.APP_TITLE}
    Powered by OpenAI GPT • Built with Gradio
    """)
    
    # Chat interface
    # COMPONENT: gr.Chatbot() - Built-in chat display
    chatbox = gr.Chatbot(
        label="Conversation",
        height=500,
        show_label=True,
        avatar_images=(None, "🤖")  # User and bot avatars
    )
    
    # Input row
    with gr.Row():
        # Text input
        # COMPONENT: gr.Textbox() - Single/multi-line input
        msg_input = gr.Textbox(
            label="Your message",
            placeholder="Type your message here...",
            lines=2,
            max_lines=5,
            show_label=False
        )
    
    # Button row
    with gr.Row():
        # Submit button
        submit_btn = gr.Button(
            "Send",
            variant="primary",  # Makes it blue/prominent
            scale=3  # Takes 3/4 of row width
        )
        
        # Clear button
        clear_btn = gr.Button(
            "Clear",
            variant="secondary",
            scale=1  # Takes 1/4 of row width
        )
    
    # Settings accordion (collapsible)
    with gr.Accordion("⚙️ Settings", open=False):
        gr.Markdown(f"""
        **Model:** {Config.MODEL_NAME}  
        **Temperature:** {Config.TEMPERATURE}  
        **Max Tokens:** {Config.MAX_TOKENS}  
        **Max History:** {Config.MAX_HISTORY} messages
        """)
    
    # Help accordion
    with gr.Accordion("ℹ️ How to Use", open=False):
        gr.Markdown("""
        1. Type your message in the text box
        2. Click "Send" or press Enter
        3. Wait for the AI response
        4. Continue the conversation
        5. Click "Clear" to start over
        """)
    
    # ========================================================================
    # STEP 4.5: Event Handlers
    # ========================================================================
    # GRADIO EVENTS: Connect components to functions
    
    # Submit button click
    # PATTERN: .click(function, inputs, outputs)
    submit_btn.click(
        fn=chat_function,           # Function to call
        inputs=[msg_input, chatbox],  # What to pass to function
        outputs=chatbox,              # What to update with result
        api_name="chat"              # Creates API endpoint
    ).then(
        # CHAINING: Clear input after sending
        fn=lambda: "",               # Return empty string
        inputs=None,
        outputs=msg_input
    )
    
    # Enter key in textbox
    # PATTERN: Same as button, for convenience
    msg_input.submit(
        fn=chat_function,
        inputs=[msg_input, chatbox],
        outputs=chatbox
    ).then(
        fn=lambda: "",
        inputs=None,
        outputs=msg_input
    )
    
    # Clear button click
    clear_btn.click(
        fn=clear_conversation,
        inputs=None,
        outputs=chatbox
    )
    
    # Footer
    gr.Markdown("""
    ---
    💡 **Tip:** Be specific in your questions  
    ⚡ **Speed:** Responses typically take 2-5 seconds  
    🔒 **Privacy:** Conversations are not stored permanently
    """)


# ============================================================================
# STEP 4.6: Launch Application
# ============================================================================
# GRADIO LAUNCH: Start web server

if __name__ == "__main__":
    """
    Launch the Gradio interface
    
    PARAMETERS:
    - share: Create public link (gradio.app)
    - server_name: "0.0.0.0" for network access
    - server_port: Port number (default: 7860)
    - debug: Show detailed errors
    - show_error: Display errors in UI
    """
    
    demo.launch(
        share=False,           # Set True for public link
        server_name="127.0.0.1",  # Localhost only
        server_port=7860,      # Default Gradio port
        debug=True,            # Show debug info
        show_error=True        # Show errors in UI
    )


# ============================================================================
# HOW TO RUN THIS APP
# ============================================================================
"""
COMMAND:
    python app_gradio.py

WHAT HAPPENS:
1. Gradio starts local web server
2. Opens browser automatically
3. Interface is ready to use
4. Creates API endpoints automatically

GRADIO FEATURES USED:
- gr.Blocks() - Custom layout
- gr.Chatbot() - Chat display
- gr.Textbox() - Text input
- gr.Button() - Action buttons
- gr.Accordion() - Collapsible sections
- gr.Row() - Horizontal layout
- .click() - Event handlers
- .submit() - Enter key handler
- .then() - Chain actions

GRADIO vs STREAMLIT COMPARISON:

GRADIO PROS:
✅ Simpler code
✅ Automatic API generation
✅ Easy public sharing
✅ Better for ML demos

STREAMLIT PROS:
✅ More UI components
✅ Better for dashboards
✅ More customization
✅ Better state management

CHOOSE GRADIO WHEN:
- Building quick demo
- Need public sharing
- Simple interface sufficient
- Want automatic API

CHOOSE STREAMLIT WHEN:
- Complex UI needed
- Dashboard-style app
- More customization required
- Internal tool (no sharing needed)
"""
