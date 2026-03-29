import streamlit as st

from chatbot_core import ChatbotCore
from config import Config

PROVIDER_LABELS = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "gemini": "Gemini",
}

st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon=Config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    if "chatbot" not in st.session_state:
        try:
            available_providers = Config.configured_providers()
            provider = st.session_state.get("provider")
            if provider not in available_providers:
                provider = Config.default_provider()
            st.session_state.provider = provider
            st.session_state.chatbot = ChatbotCore(provider=provider)
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []


initialize_session_state()

with st.sidebar:
    available_providers = Config.configured_providers()
    st.header("Settings")

    provider = st.selectbox(
        "AI Provider",
        options=available_providers,
        index=available_providers.index(st.session_state.provider),
    )

    if st.session_state.get("provider") != provider:
        st.session_state.provider = provider
        try:
            st.session_state.chatbot = ChatbotCore(provider=provider)
            st.session_state.messages = []
        except Exception as e:
            st.error(f"Failed to switch provider: {e}")

    st.info(
        f"""
    **Model:** {st.session_state.chatbot.model}  
    **Temperature:** {Config.TEMPERATURE}  
    **Max History:** {Config.MAX_HISTORY} messages
    """
    )

    st.metric(label="Messages", value=st.session_state.chatbot.get_message_count())
    st.divider()
    st.subheader("Actions")

    if st.button("Clear Conversation", type="primary", use_container_width=True):
        st.session_state.chatbot.reset_conversation()
        st.session_state.messages = []
        st.rerun()

    st.divider()

    with st.expander("How to Use"):
        st.markdown(
            """
        1. Type your message in the input box
        2. Press Enter or click Send
        3. Wait for AI response
        4. Continue conversation
        5. Click "Clear" to start over
        """
        )

    with st.expander("Debug Info"):
        st.json(
            {
                "provider": st.session_state.chatbot.provider,
                "model": st.session_state.chatbot.model,
                "message_count": st.session_state.chatbot.get_message_count(),
                "history_length": len(st.session_state.chatbot.messages),
            }
        )

st.title(f"{Config.APP_ICON} {Config.APP_TITLE}")
st.caption(
    f"Powered by {PROVIDER_LABELS.get(st.session_state.chatbot.provider, 'AI')} - Built with Streamlit"
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                st.session_state.chatbot.add_user_message(user_input)
                response = st.session_state.chatbot.get_response()
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_message = f"Error: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("Tip: Be specific in your questions")

with col2:
    st.caption("Speed: Responses typically take 2-5 seconds")

with col3:
    st.caption("Privacy: Conversations are not stored")
