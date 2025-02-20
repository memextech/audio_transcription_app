import streamlit as st
import sounddevice as sd
import numpy as np
import wavio
import tempfile
import os
import time
import queue
import matplotlib.pyplot as plt
from lightning_whisper_mlx import LightningWhisperMLX

# Page config
st.set_page_config(
    page_title="Audio Transcription",
    page_icon="🎙️",
    layout="centered"
)

# Custom CSS
st.markdown('''
<style>
    .stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px;
    }
    .recording-status {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
    }
    .recording-active {
        background-color: rgba(255, 0, 0, 0.1);
        border: 1px solid red;
        color: red;
        animation: pulse 1s infinite;
    }
    .recording-inactive {
        background-color: rgba(0, 255, 0, 0.1);
        border: 1px solid #1DB954;
        color: #1DB954;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .timer {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        color: #1DB954;
        margin: 10px 0;
    }
</style>
''', unsafe_allow_html=True)

# Initialize Whisper model
@st.cache_resource
def load_whisper_model():
    return LightningWhisperMLX(model="distil-medium.en", batch_size=12, quant=None)

# Initialize the Whisper model
whisper_model = load_whisper_model()

# Streamlit app
st.title("🎙️ Audio Transcription")
st.write("Click 'Start Recording' and speak into your microphone. Click 'Stop' when you're done.")

# Recording parameters
sample_rate = 44100

# Initialize session state
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = []
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# Create placeholders
status_placeholder = st.empty()
timer_placeholder = st.empty()
wave_placeholder = st.empty()
result_placeholder = st.empty()

# Configure matplotlib
plt.style.use('dark_background')

# Audio data queue
audio_queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

# Create columns for buttons
col1, col2 = st.columns(2)

# Display recording status
if st.session_state.recording:
    status_placeholder.markdown(
        '<div class="recording-status recording-active">🔴 Recording in progress...</div>',
        unsafe_allow_html=True
    )
    
    # Update timer if recording
    if st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        timer_placeholder.markdown(
            f'<div class="timer">⏱️ {elapsed:.2f}s</div>',
            unsafe_allow_html=True
        )
else:
    status_placeholder.markdown(
        '<div class="recording-status recording-inactive">Ready to record</div>',
        unsafe_allow_html=True
    )
    timer_placeholder.empty()

with col1:
    if st.button("🎙️ Start Recording", disabled=st.session_state.recording):
        st.session_state.recording = True
        st.session_state.start_time = time.time()
        st.session_state.audio_data = []
        
        # Clear previous results
        result_placeholder.empty()
        
        # Start audio stream
        stream = sd.InputStream(
            channels=1,
            samplerate=sample_rate,
            callback=audio_callback
        )
        stream.start()
        
        # Update the UI
        st.rerun()

with col2:
    if st.button("⏹️ Stop Recording", disabled=not st.session_state.recording):
        st.session_state.recording = False
        st.session_state.start_time = None
        
        # Stop the stream
        stream.stop()
        stream.close()
        
        # Process all remaining audio in queue
        while not audio_queue.empty():
            st.session_state.audio_data.extend(audio_queue.get()[:, 0])
        
        # Convert to numpy array
        recording = np.array(st.session_state.audio_data)
        
        if len(recording) > 0:
            # Save the recording to a temporary WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                wavio.write(temp_audio.name, recording, sample_rate, sampwidth=2)
                
                # Transcribe the audio
                with st.spinner("🔄 Transcribing..."):
                    result = whisper_model.transcribe(audio_path=temp_audio.name)
                
                # Display the transcription
                result_placeholder.success("✅ Transcription complete!")
                result_placeholder.markdown("### 📝 Transcription:")
                result_placeholder.write(result['text'])
                
                # Clean up
                os.unlink(temp_audio.name)
        
        # Update the UI
        st.rerun()

# Reset button
if st.button("🔄 Reset", disabled=st.session_state.recording):
    st.session_state.recording = False
    st.session_state.start_time = None
    st.session_state.audio_data = []
    # Clear all placeholders
    status_placeholder.empty()
    timer_placeholder.empty()
    wave_placeholder.empty()
    result_placeholder.empty()
    # Clear the audio queue
    while not audio_queue.empty():
        audio_queue.get()
    st.rerun()

# Instructions
with st.expander("ℹ️ Instructions"):
    st.write('''
    1. Click "Start Recording" to begin
    2. Speak clearly into your microphone
    3. Watch the recording status and timer
    4. Click "Stop Recording" when you're finished
    5. Wait for the transcription to complete
    6. Your transcribed text will appear below
    ''')
