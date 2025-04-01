import os
import sys
import time
import tempfile
import numpy as np
import sounddevice as sd
import wavio
import whisper
import soundfile as sf
from scipy import signal

# Set up basic logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("whisper_cli_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WhisperCLI")

def record_audio(duration=5, sample_rate=16000):
    """Record audio for the specified duration."""
    logger.info(f"Recording audio for {duration} seconds...")
    
    # Record audio
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()  # Wait until recording is finished
    
    logger.info(f"Recording complete. Captured {len(recording)} samples.")
    return recording

def save_audio_to_file(audio_data, sample_rate=16000):
    """Save audio data to a temporary WAV file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        logger.info(f"Saving audio to temporary file: {temp_audio.name}")
        wavio.write(temp_audio.name, audio_data, sample_rate, sampwidth=2)
        return temp_audio.name

def load_audio_with_soundfile(audio_path):
    """Load audio file using soundfile and prepare for Whisper."""
    logger.info(f"Loading audio from file: {audio_path}")
    audio_data, sample_rate = sf.read(audio_path)
    
    # Convert to mono if stereo
    if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
        logger.info("Converting stereo to mono")
        audio_data = audio_data.mean(axis=1)
    
    # Resample to 16kHz if needed
    if sample_rate != 16000:
        logger.info(f"Resampling from {sample_rate}Hz to 16000Hz")
        audio_data = signal.resample(audio_data, int(len(audio_data) * 16000 / sample_rate))
    
    # Convert to float32 (required by Whisper)
    if audio_data.dtype != np.float32:
        logger.info(f"Converting audio from {audio_data.dtype} to float32")
        audio_data = audio_data.astype(np.float32)
    
    logger.info(f"Audio loaded: {len(audio_data)} samples, dtype={audio_data.dtype}")
    return audio_data

def transcribe_with_whisper(audio_data, model_name="tiny"):
    """Transcribe audio data with Whisper."""
    try:
        logger.info(f"Loading Whisper model: {model_name}")
        model = whisper.load_model(model_name)
        
        logger.info(f"Transcribing audio, {len(audio_data)} samples")
        
        # Ensure audio data is float32
        if audio_data.dtype != np.float32:
            logger.info(f"Converting audio from {audio_data.dtype} to float32")
            audio_data = audio_data.astype(np.float32)
        
        # Normalize audio data to be between -1 and 1
        if np.max(np.abs(audio_data)) > 1.0:
            logger.info("Normalizing audio data")
            audio_data = audio_data / np.max(np.abs(audio_data))
        
        result = model.transcribe(audio_data)
        
        logger.info(f"Transcription result: {result['text']}")
        return result["text"]
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

def main():
    logger.info("Starting Whisper CLI test")
    
    # Test with direct audio recording
    print("Recording 5 seconds of audio...")
    audio_data = record_audio(duration=5)
    
    # Save audio to file
    print("\nSaving audio to file...")
    audio_file = save_audio_to_file(audio_data)
    
    # Load audio from file
    print("\nLoading audio from file...")
    loaded_audio = load_audio_with_soundfile(audio_file)
    
    # Transcribe loaded audio
    print("\nTranscribing audio...")
    result = transcribe_with_whisper(loaded_audio)
    print(f"Transcription result: {result}")
    
    # Clean up
    try:
        os.unlink(audio_file)
        logger.info(f"Deleted temporary file: {audio_file}")
    except Exception as e:
        logger.error(f"Error deleting temporary file: {str(e)}")
    
    logger.info("Test complete")

if __name__ == "__main__":
    main()
