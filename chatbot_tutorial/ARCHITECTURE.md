# 🏗️ Chatbot Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                  │
│                    (Web Browser)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Request
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   GUI LAYER                                  │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   Streamlit      │   OR    │     Gradio       │         │
│  │  app_streamlit.py│         │  app_gradio.py   │         │
│  │                  │         │                  │         │
│  │  - Session State │         │  - Blocks Layout │         │
│  │  - Chat Display  │         │  - Event Handlers│         │
│  │  - Input Widget  │         │  - Auto API      │         │
│  └────────┬─────────┘         └────────┬─────────┘         │
└───────────┼──────────────────────────────┼──────────────────┘
            │                              │
            │ Function Calls               │
            ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   LOGIC LAYER                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ChatbotCore                              │  │
│  │           (chatbot_core.py)                          │  │
│  │                                                       │  │
│  │  Methods:                                            │  │
│  │  - __init__()          Initialize chatbot           │  │
│  │  - add_user_message()  Add to history              │  │
│  │  - get_response()      Call API                     │  │
│  │  - reset()             Clear history                │  │
│  │  - export()            Save conversation            │  │
│  │                                                       │  │
│  │  State:                                              │  │
│  │  - messages: List[Dict]  Conversation history       │  │
│  │  - client: OpenAI/Anthropic  API client            │  │
│  │  - model: str  Model name                           │  │
│  └────────────────────┬──────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────┘
                          │
                          │ API Call
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   CONFIG LAYER                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                Config                                 │  │
│  │              (config.py)                             │  │
│  │                                                       │  │
│  │  - OPENAI_API_KEY     From .env                     │  │
│  │  - MODEL_NAME         gpt-3.5-turbo                 │  │
│  │  - TEMPERATURE        0.7                           │  │
│  │  - MAX_TOKENS         1000                          │  │
│  │  - SYSTEM_PROMPT      Behavior definition           │  │
│  │  - MAX_HISTORY        10 messages                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ HTTPS Request
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL API                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              OpenAI API                               │  │
│  │        (api.openai.com)                              │  │
│  │                                                       │  │
│  │  Endpoint: /v1/chat/completions                      │  │
│  │  Method: POST                                        │  │
│  │  Body: {model, messages, temperature, ...}          │  │
│  │  Response: {choices: [{message: {content}}]}        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. User Sends Message

```
User Types "Hello"
    │
    ▼
GUI captures input
    │
    ▼
Display user message immediately (optimistic UI)
    │
    ▼
Add to session state
    │
    ▼
Call chatbot.add_user_message("Hello")
```

### 2. Processing

```
ChatbotCore.add_user_message()
    │
    ▼
Append to messages list:
    messages.append({"role": "user", "content": "Hello"})
    │
    ▼
Trim history if needed:
    if len(messages) > MAX_HISTORY:
        messages = [system] + messages[-MAX_HISTORY:]
    │
    ▼
Call chatbot.get_response()
```

### 3. API Call

```
ChatbotCore.get_response()
    │
    ▼
Prepare API request:
    {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "Hello"}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    │
    ▼
Send to OpenAI API
    │
    ▼
Wait for response (2-5 seconds)
    │
    ▼
Receive response:
    {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "Hi! How can I help you?"
            }
        }]
    }
    │
    ▼
Extract content: response.choices[0].message.content
```

### 4. Display Response

```
Return response text to GUI
    │
    ▼
Add to messages list:
    messages.append({"role": "assistant", "content": "Hi! ..."})
    │
    ▼
Display in chat interface
    │
    ▼
Update session state
    │
    ▼
Ready for next message
```

---

## Message Structure

### In Memory (Python)
```python
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant"
    },
    {
        "role": "user",
        "content": "Hello"
    },
    {
        "role": "assistant",
        "content": "Hi! How can I help you?"
    }
]
```

### Sent to API (JSON)
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

### Received from API (JSON)
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-3.5-turbo",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hi! How can I help you?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 10,
    "total_tokens": 30
  }
}
```

---

## State Management

### Streamlit Session State
```python
st.session_state = {
    "chatbot": ChatbotCore(),  # Chatbot instance
    "messages": [              # Display messages
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"}
    ]
}
```

### ChatbotCore State
```python
self.messages = [              # API messages
    {"role": "system", "content": "..."},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi!"}
]
self.client = OpenAI(...)      # API client
self.model = "gpt-3.5-turbo"   # Model name
```

---

## Error Handling Flow

```
User sends message
    │
    ▼
Try:
    │
    ├─► Add to history
    │
    ├─► Call API
    │   │
    │   ├─► Network error?
    │   │   └─► Catch: "Network error, try again"
    │   │
    │   ├─► API error?
    │   │   └─► Catch: "API error: {message}"
    │   │
    │   ├─► Rate limit?
    │   │   └─► Catch: "Too many requests, wait"
    │   │
    │   └─► Success
    │       └─► Return response
    │
    └─► Display response
        │
        └─► Update state

Except Exception as e:
    │
    └─► Display error message
        │
        └─► Log error
            │
            └─► Continue (don't crash)
```

---

## File Dependencies

```
app_streamlit.py
    │
    ├─► imports chatbot_core.py
    │       │
    │       └─► imports config.py
    │               │
    │               └─► imports .env
    │
    └─► imports config.py

app_gradio.py
    │
    ├─► imports chatbot_core.py
    │       │
    │       └─► imports config.py
    │               │
    │               └─► imports .env
    │
    └─► imports config.py
```

---

## Deployment Architecture

### Local Development
```
Your Computer
    │
    ├─► Python Process
    │   └─► Streamlit/Gradio Server
    │       └─► http://localhost:8501
    │
    └─► Browser
        └─► Connects to localhost
```

### Production (Streamlit Cloud)
```
Streamlit Cloud
    │
    ├─► Container
    │   └─► Python + Streamlit
    │       └─► Your App
    │
    └─► Public URL
        └─► https://yourapp.streamlit.app
            │
            └─► Users connect here
```

---

## Security Architecture

```
┌─────────────────────────────────────┐
│         .env File                    │
│  OPENAI_API_KEY=sk-...              │
│  (Never committed to git)           │
└──────────────┬──────────────────────┘
               │
               │ Loaded by python-dotenv
               ▼
┌─────────────────────────────────────┐
│      Environment Variables           │
│  os.getenv("OPENAI_API_KEY")        │
└──────────────┬──────────────────────┘
               │
               │ Used by Config
               ▼
┌─────────────────────────────────────┐
│         Config Class                 │
│  API_KEY = os.getenv(...)           │
└──────────────┬──────────────────────┘
               │
               │ Used by ChatbotCore
               ▼
┌─────────────────────────────────────┐
│      OpenAI Client                   │
│  OpenAI(api_key=Config.API_KEY)     │
└──────────────┬──────────────────────┘
               │
               │ HTTPS (encrypted)
               ▼
┌─────────────────────────────────────┐
│       OpenAI API                     │
│  api.openai.com                      │
└─────────────────────────────────────┘
```

---

## Scalability Considerations

### Current (Single User)
```
1 User → 1 Browser → 1 Session → 1 ChatbotCore → OpenAI API
```

### Multi-User (Future)
```
User 1 → Browser 1 → Session 1 → ChatbotCore 1 ─┐
User 2 → Browser 2 → Session 2 → ChatbotCore 2 ─┼→ OpenAI API
User 3 → Browser 3 → Session 3 → ChatbotCore 3 ─┘
```

### With Database (Future)
```
User → Browser → Session → ChatbotCore → Database
                                │            │
                                │            └─► Load history
                                │
                                └─► OpenAI API
```

---

## Performance Metrics

### Typical Response Times
- User input to display: < 100ms
- API call: 2-5 seconds
- Total user wait: 2-5 seconds

### Resource Usage
- Memory: ~50MB per session
- CPU: Minimal (waiting on API)
- Network: ~1-5KB per message

### Cost (OpenAI GPT-3.5)
- Input: $0.0015 per 1K tokens
- Output: $0.002 per 1K tokens
- Typical message: ~100-500 tokens
- Cost per message: $0.001-0.005

---

**This is the complete architecture of your chatbot! 🏗️**
