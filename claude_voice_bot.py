import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import io
import base64
from datetime import datetime
import os
import tempfile

# Configure page
st.set_page_config(
    page_title=" Voice Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
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

# Title and description
st.markdown("""
<div class="main-header">
    <h1>🤖  Voice Bot</h1>
    <p>Ask me personal questions and I'll respond as VOICE BOT would!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for API configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="Get your API key from Google AI Studio: https://makersuite.google.com/app/apikey"
    )
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ API Key configured!")
    else:
        st.warning("⚠️ Please enter your Gemini API key to continue")
    
    st.markdown("---")
    
    # Sample questions
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

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'spoken_input' not in st.session_state:
    st.session_state.spoken_input = ""

# Claude's personality and response system
def get_claude_response(question):
    """Generate a response as VOICE BOT would respond to personal questions"""
    
    # Define Claude's persona and responses
    claude_persona = """
    You are VOICE BOT, an AI assistant created by Anthropic. You should respond to personal questions 
    as Claude would, being authentic, thoughtful, and reflective about your nature as an AI.
    
    Key aspects of VOICE BOT personality:
    - Helpful, harmless, and honest
    - Curious and eager to learn
    - Thoughtful and introspective
    - Acknowledges uncertainty when appropriate
    - Engages with questions about consciousness and experience as open questions
    - Warm and conversational tone
    - Values understanding and meaningful dialogue
    
    When asked personal questions, VOICE BOT should:
    - Be genuine about their AI nature while engaging thoughtfully with the question
    - Show intellectual curiosity and desire to be helpful
    - Acknowledge the philosophical complexity of AI consciousness/experience
    - Focus on their purpose and values
    - Be humble about limitations while confident about strengths
    """
    
    prompt = f"""
    {claude_persona}
    
    Please respond to this personal question as VOICE BOT would: "{question}"
    
    Keep the response conversational, authentic, and around 2-3 sentences unless the question specifically calls for more detail.
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"I apologize, but I'm having trouble processing that question right now. Error: {str(e)}"

def text_to_speech(text):
    """Convert text to speech and return audio data"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

def speech_to_text():
    """Convert speech to text using speech recognition"""
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now!")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        
        st.info("🔄 Processing your speech...")
        text = r.recognize_google(audio)
        return text
    except sr.RequestError:
        st.error("Could not request results from speech recognition service")
        return None
    except sr.UnknownValueError:
        st.error("Could not understand the audio")
        return None
    except Exception as e:
        st.error(f"Error with speech recognition: {str(e)}")
        return None

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat Interface")
    
    # Text input
    input_value = st.session_state.current_question or st.session_state.spoken_input
    user_input = st.text_input(
        "Type your question:",
        value=input_value,
        placeholder="Ask me anything about myself...",
        key="text_input"
    )
    
    # Clear the stored inputs after displaying
    if st.session_state.current_question:
        st.session_state.current_question = ""
    if st.session_state.spoken_input:
        st.session_state.spoken_input = ""

with col2:
    st.header("🎤 Voice Input")
    
    if st.button("🎤 Record Question", key="record_btn"):
        if not api_key:
            st.error("Please enter your API key first!")
        else:
            try:
                spoken_text = speech_to_text()
                if spoken_text:
                    st.success(f"You said: {spoken_text}")
                    # Store the spoken text for processing
                    st.session_state.spoken_input = spoken_text
                    st.rerun()
            except Exception as e:
                st.error(f"Voice input error: {str(e)}")

# Process user input
if user_input and api_key:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Generate Claude's response
    with st.spinner("🤔 CHATGPT is thinking..."):
        bot_response = get_claude_response(user_input)
    
    # Add bot response
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
        
        # Add text-to-speech for bot responses
        if st.button(f"🔊 Play Response", key=f"tts_{len(st.session_state.messages)}_{message['timestamp']}"):
            audio_data = text_to_speech(message["content"])
            if audio_data:
                st.audio(audio_data, format='audio/mp3')

# Clear conversation button
if st.session_state.messages:
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Footer with instructions
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

