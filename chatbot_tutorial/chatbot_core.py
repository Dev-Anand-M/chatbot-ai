"""
Core Chatbot Logic
==================

STEP 2: The Brain of the Chatbot
---------------------------------
This file contains the core chatbot functionality.

CONVENTIONAL ARCHITECTURE:
1. Client initialization (connect to API)
2. Message formatting (prepare for API)
3. API call (send and receive)
4. Response parsing (extract answer)
5. Error handling (graceful failures)
"""

from typing import List, Dict, Optional
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from config import Config


class ChatbotCore:
    """
    Core chatbot class that handles AI interactions
    
    DESIGN PATTERN: Singleton-like behavior
    - One instance per session
    - Maintains conversation state
    - Handles API communication
    
    WHY THIS STRUCTURE?
    - Separation of concerns (logic vs UI)
    - Easy to test
    - Can swap AI providers easily
    """
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize chatbot with AI provider
        
        Args:
            provider: "openai" or "anthropic"
            
        CONVENTION: Initialize in __init__, fail fast if invalid
        """
        self.provider = provider
        self.messages: List[Dict[str, str]] = []
        
        # Initialize AI client based on provider
        # PATTERN: Factory pattern for client creation
        if provider == "openai":
            if not Config.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not found")
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.MODEL_NAME
        elif provider == "anthropic":
            if not Config.ANTHROPIC_API_KEY:
                raise ValueError("Anthropic API key not found")
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = "claude-3-sonnet-20240229"
        elif provider == "gemini":
            if not Config.GEMINI_API_KEY:
                raise ValueError("Gemini API key not found")
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = "gemini-2.5-flash"
            # Gemini uses its own client per model
            self.client = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=Config.SYSTEM_PROMPT
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Initialize conversation with system prompt
        # CONVENTION: System message always first
        self._initialize_conversation()
    
    def _initialize_conversation(self):
        """
        Set up initial conversation state
        
        WHY SEPARATE METHOD?
        - Can reset conversation easily
        - Clear initialization logic
        - Reusable for conversation reset
        """
        self.messages = [
            {"role": "system", "content": Config.SYSTEM_PROMPT}
        ]
    
    def add_user_message(self, content: str):
        """
        Add user message to conversation history
        
        Args:
            content: User's message text
            
        CONVENTION: Validate input before adding
        """
        if not content or not content.strip():
            raise ValueError("Message cannot be empty")
        
        self.messages.append({
            "role": "user",
            "content": content.strip()
        })
        
        # Trim history if too long
        # WHY? API limits and cost management
        self._trim_history()
    
    def _trim_history(self):
        """
        Keep conversation history within limits
        
        ALGORITHM:
        1. Always keep system message (index 0)
        2. Keep last N messages
        3. Maintain user-assistant pairs
        
        WHY THIS MATTERS?
        - API has token limits
        - Costs increase with history length
        - Old context becomes less relevant
        """
        if len(self.messages) > Config.MAX_HISTORY + 1:  # +1 for system message
            # Keep system message + recent messages
            self.messages = [self.messages[0]] + self.messages[-(Config.MAX_HISTORY):]
    
    def get_response(self) -> str:
        """
        Get AI response to conversation
        
        Returns:
            AI's response text
            
        FLOW:
        1. Send messages to API
        2. Receive response
        3. Extract text
        4. Add to history
        5. Return to user
        
        ERROR HANDLING:
        - Network errors
        - API errors
        - Rate limits
        - Invalid responses
        """
        try:
            if self.provider == "openai":
                response = self._get_openai_response()
            elif self.provider == "anthropic":
                response = self._get_anthropic_response()
            elif self.provider == "gemini":
                response = self._get_gemini_response()
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            # Add assistant response to history
            # CONVENTION: Always track both sides of conversation
            self.messages.append({
                "role": "assistant",
                "content": response
            })
            
            return response
            
        except Exception as e:
            # CONVENTION: Log error and return user-friendly message
            error_msg = f"Error: {str(e)}"
            print(f"❌ API Error: {error_msg}")
            return f"Sorry, I encountered an error: {error_msg}"
    
    def _get_openai_response(self) -> str:
        """
        Get response from OpenAI API
        
        API STRUCTURE (OpenAI):
        - chat.completions.create() method
        - Pass messages array
        - Receive choices array
        - Extract message.content
        
        PARAMETERS EXPLAINED:
        - model: Which AI model to use
        - messages: Conversation history
        - temperature: Randomness (0-2)
        - max_tokens: Response length limit
        - top_p: Diversity control
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
            top_p=Config.TOP_P
        )
        
        # Extract text from response
        # STRUCTURE: response.choices[0].message.content
        return response.choices[0].message.content
    
    def _get_anthropic_response(self) -> str:
        """
        Get response from Anthropic API
        
        API STRUCTURE (Anthropic):
        - messages.create() method
        - System prompt separate from messages
        - Different response structure
        
        KEY DIFFERENCE FROM OPENAI:
        - System message passed separately
        - Must filter it from messages array
        """
        # Anthropic requires system prompt separately
        system_prompt = self.messages[0]["content"]
        conversation = self.messages[1:]  # Skip system message
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=Config.MAX_TOKENS,
            temperature=Config.TEMPERATURE,
            system=system_prompt,
            messages=conversation
        )
        
        # Extract text from response
        # STRUCTURE: response.content[0].text
        return response.content[0].text

    def _get_gemini_response(self) -> str:
        """
        Get response from Google Gemini API

        API STRUCTURE (Gemini):
        - Uses chat session (start_chat)
        - History format uses "user"/"model" roles (not "assistant")
        - send_message() sends latest message

        KEY DIFFERENCE FROM OPENAI:
        - Role is "model" instead of "assistant"
        - History passed when starting chat session
        - System prompt set at model level (not in messages)
        """
        # Gemini uses "model" instead of "assistant" as role name
        # Convert our history (skip system message at index 0)
        gemini_history = []
        for msg in self.messages[1:-1]:  # skip system + last user message
            gemini_history.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]]
            })

        # Start chat session with history
        chat = self.client.start_chat(history=gemini_history)

        # Send the latest user message
        last_user_message = self.messages[-1]["content"]
        response = chat.send_message(last_user_message)

        return response.text
    
    def reset_conversation(self):
        """
        Clear conversation history and start fresh
        
        USE CASES:
        - User clicks "Clear Chat" button
        - Starting new topic
        - Error recovery
        """
        self._initialize_conversation()
    
    def get_message_count(self) -> int:
        """
        Get number of messages in conversation
        
        Returns:
            Count excluding system message
            
        WHY USEFUL?
        - Display to user
        - Debugging
        - Analytics
        """
        return len(self.messages) - 1  # Exclude system message
    
    def export_conversation(self) -> List[Dict[str, str]]:
        """
        Export conversation history
        
        Returns:
            List of message dictionaries
            
        USE CASES:
        - Save conversation
        - Analytics
        - Debugging
        - User download feature
        """
        return self.messages.copy()


# USAGE EXAMPLE (for testing):
if __name__ == "__main__":
    """
    Test the chatbot core functionality
    
    CONVENTION: Include test code in __main__ block
    """
    print("🤖 Testing Chatbot Core...")
    
    try:
        # Initialize chatbot
        bot = ChatbotCore(provider="openai")
        
        # Send a test message
        bot.add_user_message("Hello! What can you help me with?")
        response = bot.get_response()
        
        print(f"✅ Bot Response: {response}")
        print(f"📊 Message Count: {bot.get_message_count()}")
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
