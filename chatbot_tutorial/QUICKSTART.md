# 🚀 Quick Start Guide

## Get Your Chatbot Running in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install openai python-dotenv streamlit gradio
```

### Step 2: Get API Key
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

### Step 3: Create .env File
```bash
# Create .env file in chatbot_tutorial folder
echo OPENAI_API_KEY=sk-your-key-here > .env
```

### Step 4: Run Streamlit Version
```bash
streamlit run app_streamlit.py
```

### Step 5: Start Chatting!
- Browser opens automatically
- Type message in input box
- Press Enter
- Get AI response

---

## Alternative: Run Gradio Version
```bash
python app_gradio.py
```

---

## Troubleshooting

### "No API key found"
- Check .env file exists
- Check API key is correct
- Check .env is in same folder as app

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Streamlit: Use different port
streamlit run app_streamlit.py --server.port 8502

# Gradio: Change port in code
demo.launch(server_port=7861)
```

---

## What You Built

✅ Full chatbot with GUI  
✅ Conversation memory  
✅ Error handling  
✅ Settings panel  
✅ Clear button  
✅ Production-ready code  

---

## Next: Read COMPLETE_GUIDE.md
For detailed explanations of every line of code.
