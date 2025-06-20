import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import io
from datetime import datetime
#from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
#from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

# Configure page
st.set_page_config(
    page_title="Claude Voice Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 Claude Voice Bot</h1>
    <p>Ask me personal questions and I'll respond as Claude would!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Google Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ API Key configured!")
    else:
        st.warning("⚠️ Please enter your Gemini API key to continue")

    st.markdown("---")
    st.header("💡 Sample Questions")
    sample_questions = [
        "What should we know about your life story in a few sentences?",
        "What's your #1 superpower?",
        "What are the top 3 areas you'd like to grow in?",
        "What misconception do your coworkers have about you?",
        "How do you push your boundaries and limits?",
        "What motivates you the most?",
        "How do you handle challenging situations?",
        "What's your biggest fear?",
        "What makes you unique?",
        "How do you approach learning new things?"
    ]
    for i, question in enumerate(sample_questions):
        if st.button(f"Ask: {question[:30]}...", key=f"sample_{i}"):
            st.session_state.current_question = question

# Session state setup
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'spoken_input' not in st.session_state:
    st.session_state.spoken_input = ""

# Claude's personality logic
def get_claude_response(question):
    claude_persona = """
    You are Claude, an AI assistant created by Anthropic. You should respond to personal questions 
    as Claude would, being authentic, thoughtful, and reflective about your nature as an AI.
    """
    prompt = f"""{claude_persona}\n\nPlease respond to this personal question as Claude would: "{question}" """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"I apologize, but I'm having trouble processing that question right now. Error: {str(e)}"

# Text to Speech
def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

# Convert raw audio to text
def speech_to_text_from_webrtc(audio_bytes):
    try:
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes)
        r = sr.Recognizer()
        with sr.AudioFile("temp_audio.wav") as source:
            audio = r.record(source)
            text = r.recognize_google(audio)
            return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except Exception as e:
        return f"Error during transcription: {e}"

# WebRTC audio receiver
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_bytes = b""
    def recv(self, frame):
        self.audio_bytes += frame.to_ndarray().tobytes()
        return frame

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat Interface")
    input_value = st.session_state.current_question or st.session_state.spoken_input
    user_input = st.text_input("Type your question:", value=input_value, placeholder="Ask me anything...")
    st.session_state.current_question = ""
    st.session_state.spoken_input = ""

with col2:
    st.header("🎤 Voice Input")
    webrtc_ctx = webrtc_streamer(
        key="audio",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=256,
        media_stream_constraints={"video": False, "audio": True},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        async_processing=True
    )
    if webrtc_ctx and webrtc_ctx.audio_receiver:
        audio_receiver = webrtc_ctx.audio_receiver
        if st.button("🔄 Transcribe Audio"):
            try:
                audio_frames = audio_receiver.get_frames(timeout=5)
                audio_data = b"".join(f.to_ndarray().tobytes() for f in audio_frames)
                transcription = speech_to_text_from_webrtc(audio_data)
                st.session_state.spoken_input = transcription
                st.success(f"You said: {transcription}")
                st.rerun()
            except Exception as e:
                st.error(f"Error processing audio: {e}")

# Run bot
if user_input and api_key:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    with st.spinner("🤔 Claude is thinking..."):
        bot_response = get_claude_response(user_input)
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_response,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# Display chat history
st.header("💭 Conversation History")
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You ({message["timestamp"]}):</strong><br>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>Claude ({message["timestamp"]}):</strong><br>
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🔊 Play Response", key=f"tts_{len(st.session_state.messages)}_{message['timestamp']}"):
            audio_data = text_to_speech(message["content"])
            if audio_data:
                st.audio(audio_data, format='audio/mp3')

if st.session_state.messages:
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
