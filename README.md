
# 🤖 Claude Voice Bot using Gemini API

A voice-enabled conversational bot built with **Streamlit** that answers personal-style questions as **Claude** would, using the **Google Gemini API**. It supports both **text and speech input/output**, and provides thoughtful, conversational responses in Claude’s style.

---

## 🌟 Features

- 🎤 **Voice Input**: Speak your question — the bot transcribes and responds
- 💬 **Chat Interface**: Type or select a question to ask Claude
- 🔊 **Voice Output**: Listen to Claude's response using Text-to-Speech
- 🧠 **Claude Persona**: Custom prompt tuning to emulate Claude’s helpful, thoughtful tone
- ⚙️ **Easy Setup**: Just paste your Gemini API key and start using it!

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd claude-voicebot
pip install -r requirements.txt

### 2. Run The App

```bash
streamlit run app.py
st.markdown("---")
st.markdown("""
### 🚀 How to Use:
1. **Get API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your free Gemini API key
2. **Enter API Key**: Paste it in the sidebar configuration
3. **Ask Questions**: Type your question or use voice input
4. **Listen to Responses**: Click the play button to hear Claude's responses

### 📝 Setup Instructions for Deployment:
1. Install required packages: `pip install streamlit google-generativeai speechrecognition gtts pyaudio`
2. Run the app: `streamlit run app.py`
3. For deployment on Streamlit Cloud, add packages to `requirements.txt`

**Note**: Voice input requires microphone permissions in your browser.
""")

# Requirements.txt content for easy deployment
st.markdown("---")
st.header("📦 Requirements.txt for Deployment")
st.code("""
streamlit
google-generativeai
speechrecognition
gtts
pyaudio
""", language="text")




