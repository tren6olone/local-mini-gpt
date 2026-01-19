import re
import streamlit as st
import ollama
from typing import Generator, Dict, List

# --- Page Configuration ---
st.set_page_config(
    page_title="Local Mini GPT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Modern UI ---
st.markdown("""
    <style>
    /* Clean up the main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Style the Thinking Expander to look distinct */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border-radius: 8px;
        font-size: 0.9rem;
        color: #555;
    }
    
    [data-testid="stExpander"] {
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* Message styling */
    .stChatMessage {
        gap: 1rem;
    }
    
    /* Hide Deploy button */
    .stDeployButton {
        display: none;
    }
    
    /* Header Styling */
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# --- Helper Functions ---

def get_ollama_models():
    """Fetch list of available models from local Ollama instance."""
    try:
        models_info = ollama.list()
        # Handle different response structures from older/newer ollama versions
        if 'models' in models_info:
            return [m['name'] for m in models_info['models']]
        return []
    except Exception as e:
        st.sidebar.error(f"Could not connect to Ollama. Is it running? Error: {e}")
        return []

def clean_think_tags(text):
    """Remove <think> tags for final display."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def extract_think_content(text):
    """Extract content inside <think> tags."""
    match = re.search(r'<think>(.*?)</think>', text, flags=re.DOTALL)
    return match.group(1).strip() if match else None

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "selected_model" not in st.session_state:
    st.session_state["selected_model"] = ""

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    available_models = get_ollama_models()
    
    if available_models:
        selected_model = st.selectbox(
            "Select AI Model",
            available_models,
            index=0 if available_models else None
        )
        st.session_state["selected_model"] = selected_model
    else:
        st.warning("⚠️ No models found. Please run `ollama pull deepseek-r1` in your terminal.")

    st.markdown("---")
    
    # Clear Chat Button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()
        
    st.markdown("---")
    st.caption(f"Running on Local Ollama")
    st.caption("v2.0 - Local Mini GPT")

# --- Main Interface ---

col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown(f"# <span class='main-header'>Local Mini GPT</span> 🧠", unsafe_allow_html=True)
    if st.session_state["selected_model"]:
        st.caption(f"Connected to: **{st.session_state['selected_model']}**")

# --- Chat Logic ---

def display_chat_history():
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            content = msg["content"]
            
            # Check if this is an assistant message with thinking content
            if msg["role"] == "assistant":
                think_content = extract_think_content(content)
                final_response = clean_think_tags(content)
                
                if think_content:
                    with st.expander("💭 Thought Process", expanded=False):
                        st.markdown(think_content)
                
                st.markdown(final_response)
            else:
                st.markdown(content)

display_chat_history()

# --- Input Handling ---
if prompt := st.chat_input("What's on your mind?"):
    
    if not st.session_state["selected_model"]:
        st.error("Please select a model from the sidebar first.")
        st.stop()

    # Add user message to history
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        think_buffer = ""
        is_thinking = False
        has_shown_expander = False
        
        # UI Elements for streaming
        status_container = st.status("Thinking...", expanded=True)
        
        try:
            stream = ollama.chat(
                model=st.session_state["selected_model"],
                messages=st.session_state["messages"],
                stream=True
            )
            
            # We need a dedicated placeholder for the final text, 
            # and we interact with the status container for the thinking part.
            final_text_placeholder = st.empty()
            
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                
                # Check for start of thinking
                if "<think>" in content:
                    is_thinking = True
                    continue
                
                # Check for end of thinking
                if "</think>" in content:
                    is_thinking = False
                    status_container.update(label="Thinking Complete", state="complete", expanded=False)
                    continue

                if is_thinking:
                    # We are in the thinking phase
                    think_buffer += content
                    status_container.markdown(think_buffer)
                else:
                    # We are in the response phase (or the model doesn't use thinking)
                    if not has_shown_expander and not think_buffer:
                        # If model never went into thinking mode (e.g. Llama3), close the status immediately
                        status_container.update(label="Processing...", state="complete", expanded=False)
                        has_shown_expander = True
                    
                    # If we just finished thinking, ensure status is closed (redundancy check)
                    if think_buffer and not has_shown_expander:
                         status_container.update(label="Thinking Complete", state="complete", expanded=False)
                         has_shown_expander = True

                    # Display the cleaned text (live stream)
                    # We use a simple regex approach here for live display of just the text part
                    # Note: For complex streaming, this simple split is usually sufficient
                    clean_chunk = content.replace("</think>", "") 
                    final_text_placeholder.markdown(clean_think_tags(full_response) + "▌")
            
            final_text_placeholder.markdown(clean_think_tags(full_response))
            
            # Save to history
            st.session_state["messages"].append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            status_container.update(label="Error", state="error")