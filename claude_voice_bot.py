import streamlit as st
import streamlit.components.v1 as components  # ✅ Required for custom HTML
import google.generativeai as genai
from gtts import gTTS
import io
import base64
from datetime import datetime
import hashlib

# Configure page
st.set_page_config(
    page_title="🤖 Voice Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title section
st.markdown("""
<div class="main-header">
    <h1>🤖 Voice Bot</h1>
    <p>Ask me personal questions and I'll respond as Claude would!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar: API key + sample questions
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Google Gemini API Key", type="password", help="Get it from https://makersuite.google.com/app/apikey")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ API Key configured!")
    else:
        st.warning("⚠️ Please enter your Gemini API key to continue")
    st.markdown("---")
    st.header("💡 Sample Questions")
    samples = [
        "What should we know about your life story in a few sentences?",
        "What's your #1 superpower?",
        "What are the top 3 areas you'd like to grow in?",
    ]
    for q in samples:
        if st.button(f"Ask: {q[:30]}...", key=q):
            st.session_state.current_question = q

# Session state
st.session_state.setdefault('messages', [])
st.session_state.setdefault('current_question', "")
st.session_state.setdefault('last_voice_text', "")

def get_claude_response(question):
    claude_prompt = f"""
    You are Claude, an AI by Anthropic. Respond to personal questions with warmth, curiosity, and honesty.

    Question: "{question}"
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(claude_prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        st.error(f"Speech generation failed: {str(e)}")
        return None

def render_voice_interface():
    return """
    <div style="padding: 20px; border: 2px solid #ddd; border-radius: 10px; margin: 10px 0;">
        <h4>🎤 Browser Voice Recognition</h4>
        <button id="startBtn" onclick="startRecording()" style="background: #4CAF50; color: white; padding: 12px 24px;">🎤 Start</button>
        <button id="stopBtn" onclick="stopRecording()" disabled style="background: #f44336; color: white; padding: 12px 24px;">⏹️ Stop</button>
        <div id="status" style="margin-top: 10px;"></div>
        <div id="result" style="margin: 15px 0; padding: 10px; background: #f0f8ff;">Voice recognition result will appear here...</div>
        <button id="copyBtn" onclick="copyText()" disabled style="background: #2196F3; color: white; padding: 10px 20px;">📋 Copy</button>
    </div>
    <script>
    window.addEventListener("DOMContentLoaded", function () {
        let recognition;
        let finalTranscript = '';

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.continuous = false;
            recognition.interimResults = true;

            recognition.onstart = () => {
                document.getElementById('status').innerHTML = '🎙️ Listening...';
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
            };

            recognition.onresult = (event) => {
                finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    }
                }
                document.getElementById('result').innerText = finalTranscript;
                document.getElementById('copyBtn').disabled = false;
            };

            recognition.onend = () => {
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            };

            window.startRecording = () => recognition.start();
            window.stopRecording = () => recognition.stop();
            window.copyText = () => {
                navigator.clipboard.writeText(finalTranscript);
                document.getElementById('status').innerHTML = '📋 Copied!';
                window.parent.postMessage({ type: 'voice_text', text: finalTranscript }, '*');
            };
        } else {
            document.getElementById('status').innerText = 'Speech Recognition not supported.';
        }
    });
    </script>
    """

# Chat Interface
st.header("💬 Chat Interface")
user_input = st.text_input("Type your question:", value=st.session_state.current_question, placeholder="Ask me anything...")

# Voice Input Text Field
st.markdown("### 🎤 Voice Input")
st.info("Use the recorder below, then paste the recognized text here.")
voice_result = st.text_input("Voice Recognition Result:", key="voice_result_input")

if voice_result:
    if st.button("📝 Use Voice Text"):
        st.session_state.current_question = voice_result
        st.success(f"Using voice text: {voice_result}")
        st.rerun()

# ✅ Voice interface block
components.html(render_voice_interface(), height=400)

# Audio Upload (manual option)
st.header("📁 Audio File Upload")
uploaded_file = st.file_uploader("Upload audio (mp3, wav, m4a)", type=['mp3', 'wav', 'm4a'])
if uploaded_file:
    st.audio(uploaded_file)
    st.info("Use external services like Google Speech-to-Text to transcribe and paste the result.")

# Process Question
if user_input and api_key:
    st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": datetime.now().strftime("%H:%M:%S")})
    with st.spinner("Claude is thinking..."):
        reply = get_claude_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": reply, "timestamp": datetime.now().strftime("%H:%M:%S")})

# Chat history
st.header("💭 Conversation History")
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-message user-message'><strong>You ({msg['timestamp']}):</strong><br>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-message bot-message'><strong>Claude ({msg['timestamp']}):</strong><br>{msg['content']}</div>", unsafe_allow_html=True)
        if st.button("🔊 Play", key=f"play_{i}"):
            audio = text_to_speech(msg["content"])
            if audio:
                st.audio(audio, format='audio/mp3')

# Clear button
if st.session_state.messages:
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
### 🚀 How to Use:
1. Enter Gemini API key in the sidebar.
2. Type or record your question.
3. Upload audio or use voice-to-text.
4. Listen to Claude's spoken response.
""")
