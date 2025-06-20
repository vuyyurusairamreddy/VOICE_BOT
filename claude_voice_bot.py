import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import base64
from datetime import datetime
import os
import tempfile
import hashlib

# Configure page
st.set_page_config(
    page_title="🤖 Voice Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI - using triple quotes
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
    .audio-container {
        margin: 1rem 0;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("""
<div class="main-header">
    <h1>🤖 Voice Bot</h1>
    <p>Ask me personal questions and I'll respond as Claude would!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for API configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        key="api_key_input",
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
        question_hash = hashlib.md5(question.encode()).hexdigest()
        if st.button(f"Ask: {question[:30]}...", key=f"sample_q_{question_hash}"):
            st.session_state.current_question = question

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'last_voice_text' not in st.session_state:
    st.session_state.last_voice_text = ""

def get_claude_response(question):
    """Generate a response as Claude would respond to personal questions"""
    claude_persona = """
    You are Claude, an AI assistant created by Anthropic. You should respond to personal questions 
    authentically, being thoughtful and reflective about your nature as an AI.
    
    Key aspects of Claude's personality:
    - Helpful, harmless, and honest
    - Curious and eager to learn
    - Thoughtful and introspective
    - Acknowledges uncertainty when appropriate
    - Engages with questions about consciousness and experience as open questions
    - Warm and conversational tone
    - Values understanding and meaningful dialogue
    """
    
    prompt = f"""
    {claude_persona}
    
    Please respond to this personal question as Claude would: "{question}"
    
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

def render_voice_interface():
    """Render a simple voice interface with manual copy"""
    html_code = """
    <div style="padding: 20px; border: 2px solid #ddd; border-radius: 10px; margin: 10px 0;">
        <h4>🎤 Browser Voice Recognition</h4>
        
        <button id="startBtn" onclick="startRecording()" style="
            background: #4CAF50; color: white; border: none; padding: 12px 24px; 
            border-radius: 8px; cursor: pointer; margin: 5px; font-size: 16px;">
            🎤 Start Recording
        </button>
        
        <button id="stopBtn" onclick="stopRecording()" disabled style="
            background: #f44336; color: white; border: none; padding: 12px 24px; 
            border-radius: 8px; cursor: pointer; margin: 5px; font-size: 16px;">
            ⏹️ Stop Recording
        </button>
        
        <div id="status" style="margin: 15px 0; font-weight: bold; font-size: 18px;"></div>
        
        <div id="result" style="
            margin: 15px 0; padding: 15px; background: #f0f8ff; border-radius: 8px; 
            min-height: 60px; border: 2px solid #87CEEB; font-size: 16px;
        ">Voice recognition result will appear here...</div>
        
        <button id="copyBtn" onclick="copyText()" disabled style="
            background: #2196F3; color: white; border: none; padding: 10px 20px; 
            border-radius: 8px; cursor: pointer; margin: 5px; font-size: 14px;">
            📋 Copy Text
        </button>
        
        <div id="instructions" style="
            margin: 15px 0; padding: 10px; background: #fffacd; border-radius: 8px; 
            border-left: 4px solid #ffd700; font-size: 14px;">
            <strong>Instructions:</strong><br>
            1. Click "Start Recording" and speak clearly<br>
            2. Click "Stop Recording" when done<br>
            3. Copy the recognized text<br>
            4. Paste it in the input field above<br>
            5. Or click "Auto-Fill Last Recognition" button
        </div>
    </div>

    <script>
        let recognition;
        let isRecording = false;
        let finalTranscript = '';

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onstart = function() {
                document.getElementById('status').innerHTML = '🎤 <span style="color: red;">Listening... Speak now!</span>';
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                isRecording = true;
                finalTranscript = '';
            };

            recognition.onresult = function(event) {
                let interimTranscript = '';
                finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }

                let displayText = '';
                if (finalTranscript) {
                    displayText += '<strong style="color: green;">Final:</strong> ' + finalTranscript + '<br>';
                }
                if (interimTranscript) {
                    displayText += '<em style="color: blue;">Listening:</em> ' + interimTranscript;
                }
                
                document.getElementById('result').innerHTML = displayText || 'Waiting for speech...';
                
                if (finalTranscript.trim()) {
                    document.getElementById('copyBtn').disabled = false;
                    document.getElementById('status').innerHTML = '✅ <span style="color: green;">Recognition complete! Copy the text below.</span>';
                }
            };

            recognition.onerror = function(event) {
                document.getElementById('status').innerHTML = '❌ <span style="color: red;">Error: ' + event.error + '</span>';
                resetButtons();
            };

            recognition.onend = function() {
                if (finalTranscript.trim()) {
                    document.getElementById('status').innerHTML = '✅ <span style="color: green;">Done! Copy the text and paste it above.</span>';
                } else {
                    document.getElementById('status').innerHTML = '⚠️ <span style="color: orange;">No speech detected. Try again.</span>';
                }
                resetButtons();
            };
        } else {
            document.getElementById('status').innerHTML = '❌ <span style="color: red;">Speech recognition not supported in this browser</span>';
            document.getElementById('startBtn').disabled = true;
        }

        function startRecording() {
            if (recognition && !isRecording) {
                recognition.start();
            }
        }

        function stopRecording() {
            if (recognition && isRecording) {
                recognition.stop();
            }
        }

        function resetButtons() {
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            isRecording = false;
        }

        function copyText() {
            if (finalTranscript.trim()) {
                navigator.clipboard.writeText(finalTranscript.trim()).then(function() {
                    document.getElementById('status').innerHTML = '📋 <span style="color: blue;">Text copied to clipboard! Paste it in the input field above.</span>';
                    
                    window.parent.postMessage({
                        type: 'voice_text',
                        text: finalTranscript.trim()
                    }, '*');
                    
                }).catch(function() {
                    document.getElementById('status').innerHTML = '❌ <span style="color: red;">Could not copy to clipboard. Please select and copy manually.</span>';
                    
                    const range = document.createRange();
                    range.selectNodeContents(document.getElementById('result'));
                    const selection = window.getSelection();
                    selection.removeAllRanges();
                    selection.addRange(range);
                });
            }
        }

        window.addEventListener('message', function(event) {
            if (event.data.type === 'voice_text') {
                console.log('Voice text received:', event.data.text);
            }
        });
    </script>
    """
    return html_code

# Main interface
st.header("💬 Chat Interface")

# Text input
input_value = st.session_state.current_question
user_input = st.text_input(
    "Type your question:",
    value=input_value,
    placeholder="Ask me anything about myself...",
    key="text_input"
)

if st.session_state.current_question:
    st.session_state.current_question = ""

# Voice input
st.markdown("### 🎤 Voice Input")
st.info("Use the voice recorder below, then copy and paste the recognized text into the main input field above.")

voice_result = st.text_input(
    "Voice Recognition Result:",
    placeholder="Recognized text will appear here after you copy it...",
    key="voice_result_input",
    help="After recording, copy the recognized text from below and paste it here, then click 'Use Voice Text'"
)

if voice_result:
    voice_hash = hashlib.md5(voice_result.encode()).hexdigest()
    if st.button("📝 Use Voice Text", key=f"use_voice_{voice_hash}"):
        st.session_state.current_question = voice_result
        st.success(f"✅ Using: {voice_result}")
        st.rerun()

# Voice interface
st.components.v1.html(render_voice_interface(), height=400, key="voice_interface_component")

# Audio upload
st.header("📁 Audio File Upload")
uploaded_file = st.file_uploader(
    "Upload an audio file (mp3, wav, m4a)", 
    type=['mp3', 'wav', 'm4a'],
    key="audio_uploader",
    help="Record audio on your device and upload it here for transcription"
)

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav')
    st.info("📝 Audio file uploaded! For transcription, you'll need to use external services like Google Speech-to-Text API or upload the text manually.")

# Process input
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

# Display chat
st.header("💭 Conversation History")

for i, message in enumerate(st.session_state.messages):
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
        
        col1, col2 = st.columns([1, 4])
        with col1:
            message_hash = hashlib.md5(message["content"].encode()).hexdigest()
            if st.button(f"🔊 Play", key=f"tts_{i}_{message_hash}"):
                audio_data = text_to_speech(message["content"])
                if audio_data:
                    with col2:
                        st.audio(audio_data, format='audio/mp3')

# Clear button
if st.session_state.messages:
    if st.button("🗑️ Clear Conversation", key="clear_conversation"):
        st.session_state.messages = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
### 🚀 How to Use:
1. **Get API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your free Gemini API key
2. **Enter API Key**: Paste it in the sidebar configuration
3. **Ask Questions**: 
   - Type your question in the text input
   - Use voice input (browser-based speech recognition)
   - Upload audio files for manual transcription
4. **Listen to Responses**: Click the play button to hear Claude's responses 
""")
