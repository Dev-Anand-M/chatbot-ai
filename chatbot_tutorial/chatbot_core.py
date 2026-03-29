from typing import Dict, List, Optional

from anthropic import Anthropic
import google.generativeai as genai
from openai import OpenAI

from config import Config


class ChatbotCore:
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or Config.default_provider()
        self.messages: List[Dict[str, str]] = []

        if self.provider == "openai":
            if not Config.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not found")
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.MODEL_NAME
        elif self.provider == "anthropic":
            if not Config.ANTHROPIC_API_KEY:
                raise ValueError("Anthropic API key not found")
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = "claude-3-sonnet-20240229"
        elif self.provider == "gemini":
            if not Config.GEMINI_API_KEY:
                raise ValueError("Gemini API key not found")
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = "gemini-2.5-flash"
            self.client = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=Config.SYSTEM_PROMPT,
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        self._initialize_conversation()

    def _initialize_conversation(self):
        self.messages = [{"role": "system", "content": Config.SYSTEM_PROMPT}]

    def add_user_message(self, content: str):
        if not content or not content.strip():
            raise ValueError("Message cannot be empty")
        self.messages.append({"role": "user", "content": content.strip()})
        self._trim_history()

    def _trim_history(self):
        if len(self.messages) > Config.MAX_HISTORY + 1:
            self.messages = [self.messages[0]] + self.messages[-Config.MAX_HISTORY :]

    def get_response(self) -> str:
        try:
            if self.provider == "openai":
                response = self._get_openai_response()
            elif self.provider == "anthropic":
                response = self._get_anthropic_response()
            elif self.provider == "gemini":
                response = self._get_gemini_response()
            else:
                raise ValueError(f"Unknown provider: {self.provider}")

            self.messages.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"API Error: {error_msg}")
            return f"Sorry, I encountered an error: {error_msg}"

    def _get_openai_response(self) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
            top_p=Config.TOP_P,
        )
        return response.choices[0].message.content

    def _get_anthropic_response(self) -> str:
        system_prompt = self.messages[0]["content"]
        conversation = self.messages[1:]
        response = self.client.messages.create(
            model=self.model,
            max_tokens=Config.MAX_TOKENS,
            temperature=Config.TEMPERATURE,
            system=system_prompt,
            messages=conversation,
        )
        return response.content[0].text

    def _get_gemini_response(self) -> str:
        gemini_history = []
        for msg in self.messages[1:-1]:
            gemini_history.append(
                {
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [msg["content"]],
                }
            )
        chat = self.client.start_chat(history=gemini_history)
        last_user_message = self.messages[-1]["content"]
        response = chat.send_message(last_user_message)
        return response.text

    def reset_conversation(self):
        self._initialize_conversation()

    def get_message_count(self) -> int:
        return len(self.messages) - 1

    def export_conversation(self) -> List[Dict[str, str]]:
        return self.messages.copy()


if __name__ == "__main__":
    print("Testing Chatbot Core...")
    try:
        bot = ChatbotCore(provider=Config.default_provider())
        bot.add_user_message("Hello! What can you help me with?")
        response = bot.get_response()
        print(f"Bot Response: {response}")
        print(f"Message Count: {bot.get_message_count()}")
    except Exception as e:
        print(f"Test Failed: {e}")
