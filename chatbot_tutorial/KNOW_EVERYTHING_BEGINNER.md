# Know Everything: Beginner Guide to This Chatbot Project

This is the one file to read if you want the whole project explained without jumping across seven other documents.

The project is simple at its core:

1. `config.py` loads settings and API keys.
2. `chatbot_core.py` stores conversation history and talks to the AI API.
3. `app_streamlit.py` shows the chatbot in Streamlit.
4. `app_gradio.py` shows the same chatbot idea in Gradio.

Think of it like a small restaurant:

- `config.py` is the rulebook and ingredient list.
- `chatbot_core.py` is the kitchen.
- `app_streamlit.py` and `app_gradio.py` are two different dining rooms.
- The user places an order, the kitchen prepares it, and the dining room serves it.

## 1. What Every File Does

Here is the full folder, in plain English:

- `config.py`: Central settings. API keys, model name, system prompt, limits, app title.
- `chatbot_core.py`: The actual chatbot brain. Holds messages and calls OpenAI or Anthropic.
- `app_streamlit.py`: Streamlit chat app. Best choice in this repo for a normal beginner demo.
- `app_gradio.py`: Gradio chat app. Simpler event-based alternative.
- `.env.example`: Template showing what secrets/settings belong in `.env`.
- `requirements.txt`: Python packages to install.
- `1_simple_chatbot.py`: Empty file. Placeholder only. No code inside.
- `README.md`: Chatbot theory and general fundamentals.
- `START_HERE.md`: Navigation page for the original generated docs.
- `QUICKSTART.md`: Fast setup guide.
- `COMPLETE_GUIDE.md`: Existing long explanation document.
- `ARCHITECTURE.md`: Diagrams and flow descriptions.
- `WHAT_I_DID.md`: Summary of what was built.
- `FILES_CREATED.txt`: Inventory of files.

If you only care about running the project, `QUICKSTART.md` is enough.
If you want to understand the code, read this file plus the four Python files.

## 2. The Big Picture

This is the actual runtime flow:

1. The app starts.
2. `config.py` loads environment variables from `.env`.
3. The UI file creates a `ChatbotCore` object.
4. `ChatbotCore` starts the conversation with one hidden system message.
5. The user types a message.
6. That message is added to history.
7. `ChatbotCore` sends the history to OpenAI or Anthropic.
8. The API sends back a reply.
9. The reply is added to history.
10. The UI displays the reply.

Real-life analogy:

- The system prompt is the training manual given to a new employee before customers arrive.
- The conversation history is the notebook of everything said so far.
- The AI provider is the outside expert the chatbot consults.
- The UI is just the counter where the customer talks.

## 3. `config.py`: The Control Room

`config.py` is the first important file because everything else depends on it.

### 3.1 Imports

```python
import os
from dotenv import load_dotenv
```

- `os` lets Python read environment variables.
- `load_dotenv` reads a `.env` file and loads its values into the program's environment.

Real-life analogy:
This is like unlocking a cabinet so the app can read secret labels such as API keys.

### 3.2 Loading `.env`

```python
load_dotenv()
```

This line matters a lot.

Without it:

- `OPENAI_API_KEY=...` sitting in `.env` is just text in a file.
- Python will not automatically use it.

With it:

- Values from `.env` become available through `os.getenv(...)`.

Real-life analogy:
You are taking notes from a paper sheet and putting them onto the whiteboard the team actually reads.

### 3.3 The `Config` class

```python
class Config:
```

This is a central shelf for settings.

Why use a class here?

- You can access settings as `Config.MODEL_NAME`.
- You do not need to create `config = Config()`.
- Every file can import the same values easily.

Real-life analogy:
This is a building noticeboard. Everyone reads from the same board.

### 3.4 API keys

```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

This asks the environment:

- "Do you have an OpenAI key?"
- "Do you have an Anthropic key?"

If yes, the values are stored.
If no, they become `None`.

Important beginner idea:
The app does not hardcode secrets into Python files. That is the normal safe pattern.

### 3.5 Model selection

```python
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
```

This means:

- If `MODEL_NAME` exists in `.env`, use it.
- Otherwise use `"gpt-3.5-turbo"`.

Real-life analogy:
"Use the special instructions if the manager left them; otherwise use the default plan."

### 3.6 Response settings

```python
TEMPERATURE = 0.7
MAX_TOKENS = 1000
TOP_P = 1.0
```

What they mean:

- `TEMPERATURE`: How predictable or creative the output should be.
- `MAX_TOKENS`: Roughly how long the answer is allowed to be.
- `TOP_P`: Another way to control randomness.

Beginner simplification:

- Lower temperature -> safer, more consistent answers.
- Higher temperature -> more varied, sometimes weirder answers.
- `MAX_TOKENS` is like saying "do not write more than this much."

### 3.7 The system prompt

```python
SYSTEM_PROMPT = """You are a helpful AI assistant...
```

This is the hidden instruction given to the model before the conversation starts.

It tells the model:

- be helpful
- be accurate
- be friendly
- admit uncertainty
- ask clarifying questions

Real-life analogy:
Before a support agent starts work, you give them a script telling them how to behave.

### 3.8 Conversation limit

```python
MAX_HISTORY = 10
```

This limits how many recent messages are kept in memory for API calls.

Why not keep everything forever?

- More history costs more money.
- More history means bigger requests.
- Old messages often stop being useful.

Real-life analogy:
If you carry every old receipt in your wallet forever, eventually the wallet becomes useless.

### 3.9 UI settings

```python
APP_TITLE = "AI Chatbot"
APP_ICON = "..."
THEME = "light"
```

These are just presentation settings.

Important note:
`THEME` is defined but not actually used anywhere in the current code.

### 3.10 Validation

```python
@classmethod
def validate(cls):
    if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
        raise ValueError(...)
```

This checks: "Do we have at least one API key?"

If the answer is no, it raises an error.

Why do this early?

- It is better to fail immediately with a clear message.
- It is worse to fail later in the middle of a chat.

### 3.11 Validation on import

```python
try:
    Config.validate()
except ValueError as e:
    print(...)
```

This runs validation as soon as `config.py` is imported.

Very important nuance:

- It prints a warning.
- It does **not** stop the program by re-raising the error.

So what actually happens?

- `config.py` warns early.
- Later, `ChatbotCore` still fails for real if the required key is missing.

Real-life analogy:
The front desk says "there may be a problem," but the actual work stops only when the kitchen discovers the ingredient is missing.

## 4. `chatbot_core.py`: The Brain

This file contains the actual chatbot logic. The UI files are just wrappers around it.

### 4.1 Imports

```python
from typing import List, Dict, Optional
from openai import OpenAI
from anthropic import Anthropic
from config import Config
```

- `OpenAI` and `Anthropic` are API client libraries.
- `Config` provides settings.
- `List` and `Dict` are type hints.
- `Optional` is imported but not used in the current file.

That last point is harmless, just slightly unnecessary.

### 4.2 The class

```python
class ChatbotCore:
```

This class is a single chatbot session.

Each instance stores:

- which provider is used
- the API client object
- the model name
- the full conversation history

Real-life analogy:
This is one customer-service notebook, not the whole company.

### 4.3 `__init__`: setup

```python
def __init__(self, provider: str = "openai"):
```

When you create `ChatbotCore()`, Python runs this method automatically.

It does four main things:

1. Saves the provider name.
2. Creates an empty message list.
3. Builds the right API client.
4. Starts the conversation with the system prompt.

### 4.4 Provider selection

```python
if provider == "openai":
    ...
elif provider == "anthropic":
    ...
else:
    raise ValueError(...)
```

This is simple branching.

If provider is `"openai"`:

- require `OPENAI_API_KEY`
- create `OpenAI(...)`
- use `Config.MODEL_NAME`

If provider is `"anthropic"`:

- require `ANTHROPIC_API_KEY`
- create `Anthropic(...)`
- hardcode the Anthropic model name

If provider is something else:

- reject it immediately

Important beginner nuance:
The current UI files both hardcode `provider="openai"`, so Anthropic support exists in the core but is not exposed in the actual UI.

### 4.5 Hidden conversation start

```python
self._initialize_conversation()
```

This sets the initial history to:

```python
[{"role": "system", "content": Config.SYSTEM_PROMPT}]
```

So before the user types anything, the chatbot already has one hidden message in memory.

Why?

- The AI needs behavior instructions.
- You usually do not show those instructions to the end user.

Real-life analogy:
This is the staff handbook behind the counter, not part of the public conversation.

### 4.6 Adding user messages

```python
def add_user_message(self, content: str):
```

This method does three things:

1. Rejects empty input.
2. Strips extra whitespace.
3. Appends the message to history.

The stored format is:

```python
{"role": "user", "content": "Hello"}
```

This format is the normal chat API format used by major LLM providers.

### 4.7 Trimming history

```python
self._trim_history()
```

After each user message, the code checks whether history has grown too long.

Actual code:

```python
if len(self.messages) > Config.MAX_HISTORY + 1:
    self.messages = [self.messages[0]] + self.messages[-(Config.MAX_HISTORY):]
```

What this really means:

- always keep the first message, which is the system prompt
- keep only the latest `MAX_HISTORY` other messages

Important nuance:
The comment says it maintains user-assistant pairs, but the code does not explicitly enforce pairs. It simply keeps the newest messages.

That is usually fine for a simple chatbot, but it is worth knowing.

Real-life analogy:
You keep the rulebook page and the most recent pages of the conversation notebook, then throw away older pages.

### 4.8 Getting the AI response

```python
def get_response(self) -> str:
```

This is the main method.

Flow:

1. Decide which provider-specific helper to call.
2. Ask the API for a reply.
3. Add that reply to history as an `"assistant"` message.
4. Return the reply text.

If anything fails, it catches the exception and returns an error string to the caller.

Important nuance:
This means many API failures become ordinary text responses like:

```python
"Sorry, I encountered an error: ..."
```

So the UI often receives an error message string instead of a thrown exception.

### 4.9 OpenAI response helper

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=self.messages,
    temperature=Config.TEMPERATURE,
    max_tokens=Config.MAX_TOKENS,
    top_p=Config.TOP_P
)
```

This is the actual OpenAI request.

What is being sent?

- model name
- full conversation history
- generation settings

Then the code extracts:

```python
response.choices[0].message.content
```

Beginner translation:

- `choices` is a list of candidate answers
- `[0]` means "take the first one"
- `message.content` is the actual text reply

### 4.10 Anthropic response helper

Anthropic expects a slightly different format:

- system prompt is passed separately
- the normal message list excludes that system prompt

So the code does:

```python
system_prompt = self.messages[0]["content"]
conversation = self.messages[1:]
```

Then it calls `self.client.messages.create(...)`.

Same idea, different API shape.

### 4.11 Reset, count, export

These smaller methods are utility helpers:

- `reset_conversation()`: clears history and starts again with the system prompt
- `get_message_count()`: returns count excluding the system prompt
- `export_conversation()`: returns a copy of the message list

Real-life analogy:

- reset = tear out the notebook pages and start fresh
- count = check how many public messages happened
- export = photocopy the notebook

### 4.12 The test block

```python
if __name__ == "__main__":
```

This means:

- run the test code only when this file is executed directly
- do not run it when another file imports `chatbot_core`

Why this matters:

- you can test the chatbot core by itself
- importing the file stays clean

Real-life analogy:
A machine has a self-test mode, but it only runs when you explicitly turn that mode on.

## 5. `app_streamlit.py`: The Better Beginner UI

If you are learning this project, this is the most important UI file.

### 5.1 First idea: Streamlit reruns everything

This is the single most important Streamlit concept.

Every interaction reruns the script from top to bottom.

That means:

- app opens -> script runs
- user sends message -> script runs again
- user clears chat -> script runs again

If you use normal variables only, they disappear on every rerun.

That is why this line exists:

```python
if "chatbot" not in st.session_state:
```

`st.session_state` is the memory that survives reruns.

Real-life analogy:
Regular variables are words written in sand.
`session_state` is a notebook you keep between visits.

### 5.2 Page setup

```python
st.set_page_config(...)
```

This sets browser tab title, icon, layout, and sidebar state.

Why at the top?

Streamlit expects page config before most other UI commands.

### 5.3 `initialize_session_state()`

This function sets up persistent state.

It checks for three things:

```python
if "chatbot" not in st.session_state:
if "messages" not in st.session_state:
if "show_settings" not in st.session_state:
```

What each one means:

- `chatbot`: the actual `ChatbotCore` object
- `messages`: UI-friendly message list for display
- `show_settings`: a flag prepared for UI state, but not used later in this file

Important beginner note:
`show_settings` exists but currently does nothing. It is unused leftover state.

### 5.4 The chatbot initialization block

```python
if "chatbot" not in st.session_state:
    try:
        st.session_state.chatbot = ChatbotCore(provider="openai")
    except Exception as e:
        st.error(f"Failed to initialize chatbot: {e}")
        st.stop()
```

This deserves a deep explanation.

What happens on first app load:

- `session_state` is empty
- `"chatbot" not in st.session_state` is `True`
- Streamlit creates one `ChatbotCore` object
- that object is stored in session memory

What happens on later reruns:

- `"chatbot"` is already there
- the block is skipped
- the same chatbot object is reused

Why this matters:

- the conversation survives reruns
- the API client is not recreated every time
- the user experience feels like one continuous chat

Why the `try/except`?

- missing API key
- provider setup failure
- import/config problems

Why `st.error(...)`?

- show a clean message inside the app instead of a Python crash

Why `st.stop()`?

- stop the script right there
- do not keep rendering a broken app

Real-life analogy:
If the cashier cannot even open the store in the morning, you show a sign on the door and stop taking orders.

### 5.5 Why there are two message histories

This is a common beginner confusion.

The app stores messages in two places:

1. `st.session_state.chatbot.messages`
2. `st.session_state.messages`

They are not the same job.

`st.session_state.chatbot.messages`:

- used for API calls
- includes the hidden system prompt
- belongs to the chatbot brain

`st.session_state.messages`:

- used for UI display
- contains only visible user/assistant messages
- belongs to the page

Real-life analogy:

- chatbot history = the official office record
- UI history = the customer-facing display board

### 5.6 Sidebar

The sidebar is wrapped in:

```python
with st.sidebar:
```

Everything inside appears in the side panel.

What it contains:

- settings summary
- message count metric
- clear conversation button
- help section
- debug section

#### Settings summary

```python
st.info(...)
```

This simply shows the current model, temperature, and history limit.

#### Message count

```python
st.metric(label="Messages", value=...)
```

This displays a small dashboard-style number.

It uses:

```python
st.session_state.chatbot.get_message_count()
```

So the count comes from the core chatbot, not the display list.

#### Clear button

```python
if st.button("Clear Conversation", ...):
    st.session_state.chatbot.reset_conversation()
    st.session_state.messages = []
    st.rerun()
```

Three things happen:

1. Clear the chatbot's internal history.
2. Clear the UI history.
3. Force a rerun so the screen updates immediately.

Why both resets are needed:

- if you clear only the UI, the AI still remembers old messages
- if you clear only the chatbot, old chat bubbles still stay on screen

Real-life analogy:
You need to clear both the back-office notebook and the public whiteboard.

#### Help and debug

`st.expander(...)` creates collapsible sections.

- Help explains how to use the app.
- Debug shows provider, model, message count, and raw history length.

The debug section is useful for learning because it exposes the internal state.

### 5.7 Main chat display

```python
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```

This loops over visible messages and renders each as a chat bubble.

Why `message["role"]` matters:

- `"user"` makes a user bubble
- `"assistant"` makes an assistant bubble

Why `st.markdown(...)`?

- it displays normal text well
- it can also render simple Markdown formatting

### 5.8 Chat input

```python
user_input = st.chat_input("Type your message here...")
```

This creates the input box at the bottom of the app.

Important behavior:

- when the user has not submitted anything, `user_input` is empty or falsey
- when they press Enter, `user_input` becomes the submitted text for that rerun

### 5.9 Input processing flow

The block starts here:

```python
if user_input:
```

Then the app does this in order:

1. show the user message immediately
2. add it to UI history
3. open an assistant message area
4. show a spinner
5. add the user message to `ChatbotCore`
6. get response from AI
7. show response
8. add response to UI history

Why show the user's message before the API call?

Because the interface feels responsive right away.

Real-life analogy:
A cashier repeats your order immediately before walking to the kitchen.

### 5.10 The spinner

```python
with st.spinner("Thinking..."):
```

This gives feedback during the API call.

Without it:

- the app would look frozen
- beginners often think the program broke

### 5.11 Error handling in Streamlit

Inside the input block there is another `try/except`.

Important nuance:
`ChatbotCore.get_response()` already catches many API errors and returns an error string.

So this outer `try/except` mostly catches:

- empty/invalid input from `add_user_message`
- unexpected bugs outside the core's own error handling

That means there are two layers of protection:

- core-level error handling
- UI-level error handling

That is common defensive programming.

### 5.12 Footer

The footer uses:

```python
st.columns(3)
```

This creates three columns for small status messages:

- tip
- speed expectation
- privacy note

It is not core logic. It is just UI polish.

## 6. `app_gradio.py`: The Simpler Demo UI

This file builds the same chatbot idea with Gradio instead of Streamlit.

The major design difference is this:

- Streamlit reruns the whole script
- Gradio mostly reacts through callback functions

### 6.1 Global chatbot instance

```python
chatbot = ChatbotCore(provider="openai")
```

This is created once near the top of the file.

Why?

Gradio event handlers need access to a chatbot object.

Important caveat:
This creates one shared chatbot object for the whole running app process.

For one local user, that is fine.
For multiple users, this would mix conversations together.

Real-life analogy:
Instead of giving each customer a separate notebook, everyone writes into the same notebook on the counter.

So this file is good for a simple demo, but not the best multi-user design.

### 6.2 Startup failure handling

```python
try:
    chatbot = ChatbotCore(provider="openai")
except Exception as e:
    print(...)
    exit(1)
```

If the chatbot cannot start, the program exits immediately.

Difference from Streamlit:

- Streamlit shows an in-app error and stops rendering
- Gradio prints to terminal and exits

### 6.3 `chat_function`

```python
def chat_function(message: str, history: list) -> str:
```

This is the main callback Gradio runs when the user submits a message.

It:

1. checks for empty text
2. adds the user message to the chatbot
3. gets the AI response
4. returns the response string

Important nuance:
`history` is accepted because Gradio passes it in, but this function does not really use it.

Why not?

Because `ChatbotCore` already keeps its own history internally.

So Gradio has display history, and `ChatbotCore` has conversation history, just like Streamlit had separate UI and core state.

### 6.4 `clear_conversation`

```python
def clear_conversation():
    chatbot.reset_conversation()
    return None
```

This resets the chatbot state and returns `None` so Gradio clears the chat display.

Same idea as Streamlit's clear button, just using callback return values instead of `st.rerun()`.

### 6.5 Building the page with `gr.Blocks`

```python
with gr.Blocks(...) as demo:
```

This is Gradio's container for custom layouts.

Inside it, the file creates:

- header text with `gr.Markdown`
- chat window with `gr.Chatbot`
- input box with `gr.Textbox`
- buttons with `gr.Button`
- collapsible sections with `gr.Accordion`

Real-life analogy:
`gr.Blocks` is the empty room, and the components are the furniture placed inside it.

### 6.6 The chatbox

```python
chatbox = gr.Chatbot(...)
```

This is the visible conversation component.

It has:

- a label
- fixed height
- avatars

Note:
This component manages the visible chat interface. It is separate from `ChatbotCore`, which manages the AI request history.

### 6.7 Input and buttons

`msg_input` is the textbox where the user types.

`submit_btn` sends a message.

`clear_btn` resets the chat.

The `scale` values just control button widths in the row.

### 6.8 Settings and help accordions

These do the same job as the Streamlit sidebar:

- show current settings
- show short instructions

This is informational UI only.

### 6.9 Event handlers

This is the core Gradio pattern:

```python
submit_btn.click(fn=chat_function, inputs=[msg_input, chatbox], outputs=chatbox)
```

Meaning:

- when the button is clicked
- call `chat_function`
- pass the textbox and current chat history
- update the chatbox with the returned result

Then:

```python
.then(fn=lambda: "", outputs=msg_input)
```

This runs after the first action and clears the textbox.

The Enter key path uses the same logic through `msg_input.submit(...)`.

The clear button calls `clear_conversation`.

Real-life analogy:
This is an assembly line:

1. handle the message
2. update the chat
3. clear the input box

### 6.10 Launch

```python
if __name__ == "__main__":
    demo.launch(...)
```

This starts the Gradio web server.

Important launch settings:

- `share=False`: no public Gradio link
- `server_name="127.0.0.1"`: local machine only
- `server_port=7860`: standard Gradio port
- `debug=True`: more error detail
- `show_error=True`: show errors in UI

## 7. `requirements.txt`: What Gets Installed

The file contains these packages:

- `openai`: used now
- `anthropic`: used now if you switch provider
- `python-dotenv`: used now
- `streamlit`: used now
- `gradio`: used now
- `flask`: not used in current code
- `requests`: not used in current code
- `tiktoken`: not used in current code

Important beginner takeaway:
Not every installed package is actually used yet.
Some are extra or future-facing.

Real-life analogy:
This is like buying tools for a toolbox. Some tools are used today, others are just there in case you need them later.

## 8. `.env.example`: The Secret Template

This file is not meant to be run.
It is a template to copy into `.env`.

It shows:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `MODEL_NAME`

Why keep `.env.example` but not commit real `.env`?

- templates are safe to share
- real API keys are not

Real-life analogy:
`.env.example` is a blank passport form.
`.env` is the filled passport with your actual identity.

## 9. `1_simple_chatbot.py`: Empty Placeholder

This file currently has length `0`.

That means:

- no code
- no comments
- no effect on the project

Most likely it was meant to hold a smaller beginner example and was never filled in.

## 10. The Existing Markdown Files

You asked to read all files, so here is what the non-code documents are doing.

### `README.md`

This is a theory-first overview:

- what chatbots are
- common architecture patterns
- tech stack ideas
- standard project structure

It is broader than this repo.

### `START_HERE.md`

This is a navigation page.
It tells the reader where to go next.

### `QUICKSTART.md`

This is the shortest path to running the app:

1. install packages
2. create `.env`
3. run Streamlit or Gradio

### `COMPLETE_GUIDE.md`

This is an older generated explanation document covering much of the same material as this file.

### `ARCHITECTURE.md`

This explains the layers and data flow:

- user
- GUI
- core logic
- config
- external API

### `WHAT_I_DID.md`

This is a build summary:

- what was created
- why those choices were made
- what you can extend next

### `FILES_CREATED.txt`

This is a simple inventory and status sheet.

## 11. The Most Important Beginner Confusions

### "Why is the system prompt hidden?"

Because it is an instruction to the model, not part of the user's visible conversation.

### "Why not put everything in one file?"

You could, but splitting config, core logic, and UI makes the project easier to understand and change.

### "Why do both UIs use `ChatbotCore`?"

Because the chatbot logic should live once, not be duplicated in every interface.

### "Why does Streamlit use `session_state` but Gradio does not?"

Because Streamlit reruns the whole script on interaction, so it needs explicit persistent state.
Gradio relies more on callback functions and component updates.

### "Why are there two message lists?"

Because the UI and the AI provider have slightly different needs.

- UI wants only visible chat bubbles.
- API wants the hidden system prompt too.

### "Why is there error handling in both the UI and the core?"

Because layers should protect themselves.

- the core protects API communication
- the UI protects the user experience

### "Does this project store chats permanently?"

No. The chat lives only in app memory while the app/session is running.

### "Which file should I run?"

For beginners, run:

```bash
streamlit run app_streamlit.py
```

Use Gradio only if you specifically want the alternative interface:

```bash
python app_gradio.py
```

## 12. If You Only Remember Five Things

1. `config.py` loads settings and secrets.
2. `ChatbotCore` is the real chatbot; the UI files are only wrappers.
3. The system prompt is the hidden instruction that defines behavior.
4. Streamlit needs `st.session_state` because the script reruns on every interaction.
5. Gradio's current version uses one global chatbot instance, so it is demo-friendly but not ideal for multi-user use.

## 13. Recommended Reading Order

If you are a complete beginner, use this order:

1. `KNOW_EVERYTHING_BEGINNER.md`
2. `QUICKSTART.md`
3. `config.py`
4. `chatbot_core.py`
5. `app_streamlit.py`
6. `app_gradio.py`

That order goes from concept -> setup -> brain -> UI.

## 14. Final Summary in One Paragraph

This repo is a small chatbot application with one shared backend idea and two UI choices. `config.py` defines the rules, `chatbot_core.py` stores the conversation and calls the AI model, `app_streamlit.py` wraps that logic in a session-based Streamlit interface, and `app_gradio.py` wraps it in a callback-based Gradio interface. The rest of the files are setup templates or duplicated documentation around that same core idea. If you understand those four Python files and the difference between config, state, and UI, you understand this project.
