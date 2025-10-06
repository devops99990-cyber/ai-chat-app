import streamlit as st
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="AI Chat App",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS
st.markdown("""
<style>
    .stTextInput>div>div>input {
        border-radius: 20px;
    }
    .stButton>button {
        border-radius: 20px;
        width: 100%;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #2196F3;
    }
    .chat-message.assistant {
        background-color: #f0f0f0;
        border-left: 5px solid #9e9e9e;
    }
    .chat-message .message-content {
        display: flex;
        margin-top: 0.5rem;
    }
    .model-info {
        font-size: 0.8rem;
        color: #666;
        text-align: right;
        font-style: italic;
    }
    .error-message {
        color: #d32f2f;
        font-size: 0.9rem;
        padding: 0.5rem;
        background-color: #ffebee;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_model" not in st.session_state:
    st.session_state.current_model = "Loading..."

if "error" not in st.session_state:
    st.session_state.error = None

# App title
st.title("🧠 AI Chat App")

# Sidebar with model information
with st.sidebar:
    st.header("Model Information")
    st.write(f"Current model: **{st.session_state.current_model}**")
    
    if st.button("Refresh Model Info"):
        try:
            response = requests.get(f"{BACKEND_URL}/models")
            if response.status_code == 200:
                data = response.json()
                st.session_state.current_model = data["current_model"]
                st.success("Model information updated!")
            else:
                st.error("Failed to fetch model information")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.divider()
    st.markdown("""
    ### About
    This app uses OpenRouter to access multiple AI models:
    - Meta LLaMA 3.3 (70B, 8B)
    - Qwen 2.5 (32B, 72B)
    - Mistral (7B)
    - Google Gemma 2 (9B)
    
    The system automatically rotates models if one fails.
    """)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant" and "model" in message:
            st.markdown(f"<div class='model-info'>Model: {message['model']}</div>", unsafe_allow_html=True)

# Display error message if any
if st.session_state.error:
    st.error(st.session_state.error)
    if st.button("Clear Error"):
        st.session_state.error = None
        st.rerun()

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Display assistant thinking message
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        # Prepare chat history for API
        history = []
        for msg in st.session_state.messages[:-1]:  # Exclude the latest user message
            entry = {}
            if msg["role"] == "user":
                entry["user"] = msg["content"]
            else:
                entry["assistant"] = msg["content"]
            history.append(entry)
        
        # Send request to backend
        try:
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={"message": user_input, "history": history},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_response = data["response"]
                model_used = data["model_used"]
                
                # Update the placeholder with the actual response
                message_placeholder.markdown(assistant_response)
                
                # Add assistant message to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": assistant_response,
                    "model": model_used
                })
                
                # Update current model
                st.session_state.current_model = model_used
                
                # Clear any previous errors
                st.session_state.error = None
                
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                message_placeholder.markdown(f"<div class='error-message'>{error_msg}</div>", unsafe_allow_html=True)
                st.session_state.error = error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Request timed out. The server might be busy or unavailable."
            message_placeholder.markdown(f"<div class='error-message'>{error_msg}</div>", unsafe_allow_html=True)
            st.session_state.error = error_msg
            
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            message_placeholder.markdown(f"<div class='error-message'>{error_msg}</div>", unsafe_allow_html=True)
            st.session_state.error = error_msg

# Footer
st.markdown("---")
st.markdown("Built with Streamlit + FastAPI + OpenRouter")