import streamlit as st
import tempfile
import os
import time
from agent import VoiceToImageAgent

# Page configuration
st.set_page_config(
    page_title="Voice into Imagination",
    page_icon="🎙️",
    layout="wide"
)

# Custom CSS for refined chat style and bottom bar
st.markdown("""
<style>
    /* Fix input at bottom */
    .stChatInput {
        position: fixed;
        bottom: 3rem;
        z-index: 1000;
    }
    
    /* Hide some Streamlit elements for cleaner look */
    .element-container:has(#button-after) {
        display: none;
    }

    /* Status Container Styling */
    div[data-testid="stStatusWidget"] {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ Voice into Imagination")

# Initialize agent
if "agent" not in st.session_state:
    st.session_state.agent = VoiceToImageAgent()

agent = st.session_state.agent

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize persistent logs
if "logs" not in st.session_state:
    st.session_state.logs = []

# Initialize audio input key counter for resetting
if "audio_key_count" not in st.session_state:
    st.session_state.audio_key_count = 0

# Sidebar for Logs
with st.sidebar:
    st.title("🛠️ System Logs")
    # Display all previous logs
    log_placeholder = st.empty()
    
    with log_placeholder.container():
        for log in st.session_state.logs:
            st.caption(f"INFO: {log}")

def log_message(message):
    st.session_state.logs.append(message)
    # Refresh log view
    with log_placeholder.container():
        for log in st.session_state.logs:
            st.caption(f"INFO: {log}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            if "image_url" in message:
                st.image(message["image_url"], width="stretch")
                # Removed caption showing prompt text to keep UI clean
            else:
                st.markdown(message["content"])

# Bottom Input Area
# We use a container to hold our custom status area + the audio input
bottom_container = st.container()

with bottom_container:
    # 1. Status Area (Dynamic)
    status_placeholder = st.empty()

    # 2. Audio Input
    # Using a dynamic key allows us to reset/clear the component by incrementing the counter
    audio_key = f"audio_{st.session_state.audio_key_count}"
    audio_value = st.audio_input("Recorder", key=audio_key)

if audio_value:
    # Process the audio
    
    with st.spinner("Processing..."):
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_value.getvalue())
            audio_path = f.name
        
        try:
            # STATUS: Transcribing
            status_placeholder.info("🎙️ Transcribing voice...")
            log_message("Audio received. Transcribing...")
            transcript = agent.transcribe(audio_path)
            
            # STATUS: Show Transcript (Simulate appearing on label/near input)
            status_placeholder.success(f"🗣️ You said: \"{transcript}\"")
            log_message(f"Transcript: {transcript}")
            
            # Simulate "automatic send" pause
            time.sleep(2)
            
            # STATUS: Generating
            status_placeholder.info("🎨 Generating image...")
            log_message("Generating image prompt...")
            prompt = agent.text_to_prompt(transcript)
            
            log_message(f"Prompt: {prompt}")
            log_message("Generating image...")
            image_url = agent.generate_image(prompt)
            log_message("Image generated successfully.")
            
            # Clear Status
            status_placeholder.empty()
            
            # Update Chat History
            st.session_state.messages.append({"role": "user", "content": transcript})
            st.session_state.messages.append({"role": "assistant", "content": prompt, "image_url": image_url})

            # Increment key to reset audio input
            st.session_state.audio_key_count += 1
            
            # Rerun to update the view
            st.rerun()

        except Exception as e:
            st.error(f"An error occurred: {e}")
            log_message(f"ERROR: {e}")
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
