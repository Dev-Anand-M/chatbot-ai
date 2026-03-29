import gradio as gr

from chatbot_core import ChatbotCore
from config import Config

PROVIDER_LABELS = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "gemini": "Gemini",
}

try:
    chatbot = ChatbotCore(provider=Config.default_provider())
except Exception as e:
    print(f"Failed to initialize: {e}")
    exit(1)


def chat_function(message: str, history: list):
    history = history or []
    if not message or not message.strip():
        return history

    try:
        chatbot.add_user_message(message)
        response = chatbot.get_response()
    except Exception as e:
        response = f"Error: {str(e)}"

    history.append((message, response))
    return history


def clear_conversation():
    chatbot.reset_conversation()
    return []


with gr.Blocks(title=Config.APP_TITLE, theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        f"""
    # {Config.APP_ICON} {Config.APP_TITLE}
    Powered by {PROVIDER_LABELS.get(chatbot.provider, "AI")} - Built with Gradio
    """
    )

    chatbox = gr.Chatbot(
        label="Conversation",
        height=500,
        show_label=True,
        avatar_images=(None, Config.APP_ICON),
    )

    with gr.Row():
        msg_input = gr.Textbox(
            label="Your message",
            placeholder="Type your message here...",
            lines=2,
            max_lines=5,
            show_label=False,
        )

    with gr.Row():
        submit_btn = gr.Button("Send", variant="primary", scale=3)
        clear_btn = gr.Button("Clear", variant="secondary", scale=1)

    with gr.Accordion("Settings", open=False):
        gr.Markdown(
            f"""
        **Model:** {chatbot.model}  
        **Temperature:** {Config.TEMPERATURE}  
        **Max Tokens:** {Config.MAX_TOKENS}  
        **Max History:** {Config.MAX_HISTORY} messages
        """
        )

    with gr.Accordion("How to Use", open=False):
        gr.Markdown(
            """
        1. Type your message in the text box
        2. Click "Send" or press Enter
        3. Wait for the AI response
        4. Continue the conversation
        5. Click "Clear" to start over
        """
        )

    submit_btn.click(
        fn=chat_function,
        inputs=[msg_input, chatbox],
        outputs=chatbox,
        api_name="chat",
    ).then(fn=lambda: "", inputs=None, outputs=msg_input)

    msg_input.submit(
        fn=chat_function,
        inputs=[msg_input, chatbox],
        outputs=chatbox,
    ).then(fn=lambda: "", inputs=None, outputs=msg_input)

    clear_btn.click(
        fn=clear_conversation,
        inputs=None,
        outputs=chatbox,
    )

    gr.Markdown(
        """
    ---
    **Tip:** Be specific in your questions  
    **Speed:** Responses typically take 2-5 seconds  
    **Privacy:** Conversations are not stored permanently
    """
    )


if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860,
        debug=True,
        show_error=True,
    )
