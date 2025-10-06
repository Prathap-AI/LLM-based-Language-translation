import streamlit as st
import requests
import json
import base64
from datetime import datetime
import io
import pyttsx3
import speech_recognition as sr
import os

# Page configuration
st.set_page_config(
    page_title="LinguaBridge AI",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1A237E;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #F5F7FA;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        max-height: 400px;
        overflow-y: auto;
    }
    .user-message {
        background-color: #00B0FF;
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 0 18px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        text-align: right;
    }
    .bot-message {
        background-color: white;
        color: #333333;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 0;
        margin: 8px 0;
        max-width: 80%;
        border: 1px solid #E0E0E0;
    }
    .language-info {
        font-size: 0.8rem;
        color: #666666;
        margin-top: 4px;
    }
    .stButton button {
        background-color: #00B0FF;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: 500;
    }
    .feature-button {
        background-color: #F5F7FA !important;
        color: #1A237E !important;
        border: 1px solid #E0E0E0 !important;
    }
    .sidebar .sidebar-content {
        background-color: #F8F9FA;
    }
</style>
""", unsafe_allow_html=True)

# Language options
LANGUAGES = {
    "English": "en",
    "Spanish": "es", 
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Hindi": "hi"
}

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'conversations' not in st.session_state:
    st.session_state.conversations = {}

def translate_text(text, source_lang, target_lang):
    """
    Mock translation function - replace with actual translation API
    For demo purposes, we'll simulate translation by reversing text
    """
    # In a real app, you would use Google Translate API, DeepL, etc.
    # Example: return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    
    # Simulate API delay
    import time
    time.sleep(0.5)
    
    # Mock translation (reverse text for demo)
    return text[::-1] + f" [{source_lang}→{target_lang}]"

def text_to_speech(text):
    """Convert text to speech"""
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except:
        st.warning("Text-to-speech not available in this environment")

def speech_to_text():
    """Convert speech to text"""
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Speak now")
            audio = r.listen(source)
            text = r.recognize_google(audio)
            return text
    except:
        st.error("Speech recognition not available")
        return ""

def download_chat_history():
    """Generate downloadable chat history"""
    history_text = "LinguaBridge AI - Chat History\n\n"
    for msg in st.session_state.chat_history:
        role = "You" if msg["role"] == "user" else "Translation"
        history_text += f"{role}: {msg['content']}\n"
        if "languages" in msg:
            history_text += f"Languages: {msg['languages']}\n"
        history_text += f"Time: {msg['timestamp']}\n\n"
    
    return history_text

# Header Section
st.markdown('<div class="main-header">🌐 LinguaBridge AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Professional AI-Powered Translation Chatbot</div>', unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🎯 Translation Settings")
    
    # Language selection
    source_lang = st.selectbox(
        "From Language:",
        options=list(LANGUAGES.keys()),
        index=0,
        key="source_lang"
    )
    
    target_lang = st.selectbox(
        "To Language:",
        options=list(LANGUAGES.keys()),
        index=1,
        key="target_lang"
    )
    
    # Swap languages button
    if st.button("🔄 Swap Languages", use_container_width=True):
        if 'source_lang' in st.session_state and 'target_lang' in st.session_state:
            current_source = st.session_state.source_lang
            st.session_state.source_lang = st.session_state.target_lang
            st.session_state.target_lang = current_source
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎙️ Input Methods")
    
    # Input method selection
    input_col1, input_col2 = st.columns(2)
    with input_col1:
        text_input = st.button("📝 Text Input", use_container_width=True, type="primary")
    with input_col2:
        voice_input = st.button("🎤 Voice Input", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ⚡ Features")
    
    # Feature buttons
    if st.button("🔊 Speak Translation", use_container_width=True, key="tts"):
        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
            text_to_speech(st.session_state.chat_history[-1]["content"])
    
    if st.button("💾 Save Conversation", use_container_width=True):
        if st.session_state.chat_history:
            conv_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.conversations[conv_id] = {
                "history": st.session_state.chat_history.copy(),
                "languages": f"{source_lang} → {target_lang}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.success("Conversation saved!")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

with col2:
    st.markdown("### 💬 Translation Chat")
    
    # Chat container
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                if "languages" in message:
                    st.markdown(f'<div class="language-info" style="text-align: right;">{message["languages"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown("### ✍️ Your Message")
    
    # Voice input handling
    if voice_input:
        voice_text = speech_to_text()
        if voice_text:
            st.session_state.last_voice_input = voice_text
    
    # Text input with voice prefill
    user_input = st.text_area(
        "Enter text to translate:",
        value=st.session_state.get('last_voice_input', ''),
        height=100,
        key="user_input",
        placeholder="Type or use voice input to enter text for translation..."
    )
    
    # Translate button
    if st.button("🚀 Translate", use_container_width=True, type="primary"):
        if user_input.strip():
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input,
                "languages": f"{source_lang} → {target_lang}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # Get translation
            with st.spinner("Translating..."):
                translated_text = translate_text(
                    user_input, 
                    LANGUAGES[source_lang], 
                    LANGUAGES[target_lang]
                )
            
            # Add assistant message to history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": translated_text,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # Clear input and voice memory
            if 'last_voice_input' in st.session_state:
                del st.session_state.last_voice_input
            st.rerun()

# Sidebar for conversation history
with st.sidebar:
    st.markdown("### 📚 Conversation History")
    
    if st.session_state.conversations:
        for conv_id, conv_data in list(st.session_state.conversations.items())[-5:]:  # Show last 5
            if st.button(f"{conv_data['languages']} - {conv_data['timestamp']}", key=conv_id):
                st.session_state.chat_history = conv_data["history"].copy()
                st.rerun()
    else:
        st.info("No saved conversations yet")
    
    st.markdown("---")
    st.markdown("### 📊 Export")
    
    # Download chat history
    if st.session_state.chat_history:
        chat_text = download_chat_history()
        st.download_button(
            label="📥 Download Chat History",
            data=chat_text,
            file_name=f"translation_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "LinguaBridge AI • Professional Translation Services • Powered by AI"
    "</div>",
    unsafe_allow_html=True
)