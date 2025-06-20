import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import base64
from datetime import datetime
import os
import tempfile

# Configure page
st.set_page_config(
    page_title="🤖 Voice Bot",
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
if 'last_voice_text' not in st.session_state:
    st.session_state.last_voice_text = ""

# Claude's personality and response system
def get_claude_response(question):
    """Generate a response as Claude would respond to personal questions"""
    
    # Define Claude's persona and responses
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
    
    When asked personal questions, Claude should:
    - Be genuine about their AI nature while engaging thoughtfully with the question
    - Show intellectual curiosity and desire to be helpful
    - Acknowledge the philosophical complexity of AI consciousness/experience
    - Focus on their purpose and values
    - Be humble about limitations while confident about strengths
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

# Simplified voice input using session state
def render_voice_interface():
    """Render a simple voice interface with manual copy"""
    # Simple HTML5 voice recorder
    html_code = f"""
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

        // Initialize speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onstart = function() {{
                document.getElementById('status').innerHTML = '🎤 <span style="color: red;">Listening... Speak now!</span>';
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                isRecording = true;
                finalTranscript = '';
            }};

            recognition.onresult = function(event) {{
                let interimTranscript = '';
                finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {{
                    if (event.results[i].isFinal) {{
                        finalTranscript += event.results[i][0].transcript;
                    }} else {{
                        interimTranscript += event.results[i][0].transcript;
                    }}
                }}

                let displayText = '';
                if (finalTranscript) {{
                    displayText += '<strong style="color: green;">Final:</strong> ' + finalTranscript + '<br>';
                }}
                if (interimTranscript) {{
                    displayText += '<em style="color: blue;">Listening:</em> ' + interimTranscript;
                }}
                
                document.getElementById('result').innerHTML = displayText || 'Waiting for speech...';
                
                if (finalTranscript.trim()) {{
                    document.getElementById('copyBtn').disabled = false;
                    document.getElementById('status').innerHTML = '✅ <span style="color: green;">Recognition complete! Copy the text below.</span>';
                }}
            }};

            recognition.onerror = function(event) {{
                document.getElementById('status').innerHTML = '❌ <span style="color: red;">Error: ' + event.error + '</span>';
                resetButtons();
            }};

            recognition.onend = function() {{
                if (finalTranscript.trim()) {{
                    document.getElementById('status').innerHTML = '✅ <span style="color: green;">Done! Copy the text and paste it above.</span>';
                }} else {{
                    document.getElementById('status').innerHTML = '⚠️ <span style="color: orange;">No speech detected. Try again.</span>';
                }}
                resetButtons();
            }};
        }} else {{
            document.getElementById('status').innerHTML = '❌ <span style="color: red;">Speech recognition not supported in this browser</span>';
            document.getElementById('startBtn').disabled = true;
        }}

        function startRecording() {{
            if (recognition && !isRecording) {{
                recognition.start();
            }}
        }}

        function stopRecording() {{
            if (recognition && isRecording) {{
                recognition.stop();
            }}
        }}

        function resetButtons() {{
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            isRecording = false;
        }}

        function copyText() {{
            if (finalTranscript.trim()) {{
                navigator.clipboard.writeText(finalTranscript.trim()).then(function() {{
                    document.getElementById('status').innerHTML = '📋 <span style="color: blue;">Text copied to clipboard! Paste it in the input field above.</span>';
                    
                    // Try to store in session state for auto-fill button
                    window.parent.postMessage({{
                        type: 'voice_text',
                        text: finalTranscript.trim()
                    }}, '*');
                    
                }}).catch(function() {{
                    document.getElementById('status').innerHTML = '❌ <span style="color: red;">Could not copy to clipboard. Please select and copy manually.</span>';
                    
                    // Select the text for manual copying
                    const range = document.createRange();
                    range.selectNodeContents(document.getElementById('result'));
                    const selection = window.getSelection();
                    selection.removeAllRanges();
                    selection.addRange(range);
                }});
            }}
        }}

        // Listen for messages from parent
        window.addEventListener('message', function(event) {{
            if (event.data.type === 'voice_text') {{
                // This could be used for session state if needed
                console.log('Voice text received:', event.data.text);
            }}
        }});
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

# Clear the stored input after displaying
if st.session_state.current_question:
    st.session_state.current_question = ""

# Voice input with simple manual process
st.markdown("### 🎤 Voice Input")
st.info("Use the voice recorder below, then copy and paste the recognized text into the main input field above.")

# Manual text input for voice results
voice_result = st.text_input(
    "Voice Recognition Result:",
    placeholder="Recognized text will appear here after you copy it...",
    key="voice_result_input",
    help="After recording, copy the recognized text from below and paste it here, then click 'Use Voice Text'"
)

if voice_result:
    if st.button("📝 Use Voice Text", key="use_voice_btn"):
        st.session_state.current_question = voice_result
        st.success(f"✅ Using: {voice_result}")
        st.rerun()

# Voice input section - render the HTML interface
st.components.v1.html(render_voice_interface(), height=400)

# Alternative file upload for audio
st.header("📁 Audio File Upload")
uploaded_file = st.file_uploader(
    "Upload an audio file (mp3, wav, m4a)", 
    type=['mp3', 'wav', 'm4a'],
    help="Record audio on your device and upload it here for transcription"
)

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav')
    st.info("📝 Audio file uploaded! For transcription, you'll need to use external services like Google Speech-to-Text API or upload the text manually.")

# Process user input
if user_input and api_key:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Generate Claude's response
    with st.spinner("🤔 Claude is thinking..."):
        bot_response = get_claude_response(user_input)
    
    # Add bot response
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_response,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# Display chat history
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
        
        # Add text-to-speech for bot responses
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button(f"🔊 Play", key=f"tts_{i}_{message['timestamp']}"):
                audio_data = text_to_speech(message["content"])
                if audio_data:
                    with col2:
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
3. **Ask Questions**: 
   - Type your question in the text input
   - Use voice input (browser-based speech recognition)
   - Upload audio files for manual transcription
4. **Listen to Responses**: Click the play button to hear Claude's responses

### 📝 Setup Instructions for Deployment:

**requirements.txt:**
```
streamlit
google-generativeai
gtts
```

**For local development with voice input:**
```
streamlit
google-generativeai
gtts
speechrecognition
pyaudio
```

### 🔧 Voice Input Options:
- **Browser Speech Recognition**: Works in Chrome, Safari, and Edge
- **Audio File Upload**: Record on your device and upload
- **Text Input**: Always available as backup

**Note**: Browser speech recognition requires HTTPS in production and microphone permissions.
""")
