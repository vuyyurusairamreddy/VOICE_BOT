
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

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/claude-voicebot.git
cd claude-voicebot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure `pyaudio` is installed correctly for microphone input. On some systems, you may need to install it separately:

```bash
pip install pipwin
pipwin install pyaudio
```

### 3. Run the App

```bash
streamlit run app.py
```

---

## 💡 How to Use

1. **Get Your Gemini API Key**  
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)  
   - Copy your API key  

2. **Paste API Key into App Sidebar**

3. **Ask Questions**  
   - Use microphone or type a message  

4. **Listen to Responses**  
   - Click the play button to hear the response  

> 🎙️ *Note: Make sure to grant microphone permission in your browser.*

---

## 📝 Requirements.txt

For deployment on Streamlit Cloud or local setup:

```text
streamlit
google-generativeai
speechrecognition
gtts
pyaudio
```

---

## 🌐 Deployment on Streamlit Cloud

1. Push this repo to GitHub  
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)  
3. Connect your GitHub and deploy the app  
4. Done! ✅

---

## 📄 License

This project is licensed under the **MIT License** – feel free to fork and use!

---

## 🙌 Acknowledgements

- [Google Gemini API](https://ai.google.dev/)
- [Streamlit](https://streamlit.io/)
- [gTTS - Google Text-to-Speech](https://pypi.org/project/gTTS/)
- [SpeechRecognition Library](https://pypi.org/project/SpeechRecognition/)

---

> Made with ❤️ by [SAIRAMREDDY VUYYURU]



