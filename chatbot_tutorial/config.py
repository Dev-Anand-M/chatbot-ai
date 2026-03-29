"""
Configuration file for chatbot
================================

STEP 1: Configuration Management
---------------------------------
Every chatbot needs configuration to:
1. Store API keys securely
2. Define model parameters
3. Set system behavior
4. Manage environment-specific settings

CONVENTIONAL METHOD:
- Use environment variables for secrets
- Use config files for non-sensitive settings
- Never hardcode API keys in code
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This is the STANDARD way to handle secrets
load_dotenv()


class Config:
    """
    Configuration class using class variables
    
    WHY CLASS-BASED CONFIG?
    - Easy to access: Config.API_KEY
    - Can be inherited for different environments
    - Type hints for IDE support
    """
    
    # API Configuration
    # -----------------
    # CONVENTION: Always use environment variables for API keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Model Selection
    # ---------------
    # DEFAULT: gpt-3.5-turbo (fastest, cheapest)
    # ALTERNATIVES: gpt-4 (smarter), gpt-4-turbo (balanced)
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    
    # Model Parameters
    # ----------------
    # These control how the AI responds
    
    # Temperature: 0.0 to 2.0
    # - 0.0 = Deterministic, focused, consistent
    # - 1.0 = Balanced (DEFAULT for most chatbots)
    # - 2.0 = Creative, random, unpredictable
    TEMPERATURE = 0.7
    
    # Max Tokens: Maximum response length
    # - gpt-3.5-turbo: 4096 max
    # - gpt-4: 8192 max
    # DEFAULT: 1000 (good for chat responses)
    MAX_TOKENS = 1000
    
    # Top P: Nucleus sampling (0.0 to 1.0)
    # - Controls diversity of word choice
    # - DEFAULT: 1.0 (consider all possibilities)
    TOP_P = 1.0
    
    # System Prompt
    # -------------
    # MOST IMPORTANT: Defines chatbot personality and behavior
    # CONVENTION: Clear, specific instructions
    SYSTEM_PROMPT = """You are a helpful AI assistant. 
You provide clear, accurate, and friendly responses.
You admit when you don't know something.
You ask clarifying questions when needed."""
    
    # Conversation Settings
    # ---------------------
    # MAX_HISTORY: How many messages to remember
    # DEFAULT: 10 (5 user + 5 assistant pairs)
    # WHY LIMIT? API costs and context window limits
    MAX_HISTORY = 10
    
    # GUI Settings
    # ------------
    APP_TITLE = "AI Chatbot"
    APP_ICON = "🤖"
    THEME = "light"  # or "dark"
    
    # Validation
    # ----------
    @classmethod
    def configured_providers(cls):
        """
        Return the providers that have API keys configured.
        """
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
        """
        Return the first configured provider to use as the initial default.
        """
        providers = cls.configured_providers()
        if not providers:
            raise ValueError(
                "No API key found! Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY "
                "in .env file or environment variables."
            )
        return providers[0]

    @classmethod
    def validate(cls):
        """
        Validate configuration before starting app
        CONVENTION: Fail fast if config is invalid
        """
        if not cls.configured_providers():
            raise ValueError(
                "No API key found! Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY "
                "in .env file or environment variables."
            )
        return True


# Validate on import
# CONVENTION: Catch config errors early
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration Error: {e}")
    print("💡 Create a .env file with your API key")
