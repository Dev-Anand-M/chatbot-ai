import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    TEMPERATURE = 0.7
    MAX_TOKENS = 1000
    TOP_P = 1.0
    SYSTEM_PROMPT = """You are a helpful AI assistant.
You provide clear, accurate, and friendly responses.
You admit when you don't know something.
You ask clarifying questions when needed."""
    MAX_HISTORY = 10
    APP_TITLE = "AI Chatbot"
    APP_ICON = "🤖"
    THEME = "light"

    @classmethod
    def configured_providers(cls):
        providers = []
        if cls.OPENAI_API_KEY:
            providers.append("openai")
        if cls.ANTHROPIC_API_KEY:
            providers.append("anthropic")
        if cls.GEMINI_API_KEY:
            providers.append("gemini")
        return providers

    @classmethod
    def default_provider(cls):
        providers = cls.configured_providers()
        if not providers:
            raise ValueError(
                "No API key found! Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY "
                "in .env file or environment variables."
            )
        return providers[0]

    @classmethod
    def validate(cls):
        if not cls.configured_providers():
            raise ValueError(
                "No API key found! Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY "
                "in .env file or environment variables."
            )
        return True


try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Create a .env file with your API key")
