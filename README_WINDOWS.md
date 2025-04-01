# Audio Transcriber for Windows - Implementation Guide

This is a Windows adaptation of the macOS Audio Transcriber application, providing instant audio transcription using OpenAI's Whisper model.

## Implementation Overview

The original macOS application used Apple Silicon-specific technologies (MLX and rumps). This Windows adaptation replaces those with cross-platform alternatives while maintaining the core functionality.

### Key Changes from macOS Version

1. **GUI Framework**: 
   - Replaced macOS-specific `rumps` with cross-platform `PyQt5`
   - Implemented both system tray and windowed interfaces

2. **Speech Recognition**:
   - Replaced Apple-specific `lightning-whisper-mlx` with standard `openai-whisper`
   - Modified audio processing to work without FFmpeg dependency

3. **Audio Processing**:
   - Used `sounddevice` for audio recording (cross-platform)
   - Implemented direct audio processing with `numpy` and `soundfile`

## System Requirements

- Windows 10 or later
- Python 3.11 or later
- Microphone for audio input

## Installation Steps

### 1. Install Python

If you don't have Python installed:
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, make sure to check "Add Python to PATH"

### 2. Setup Virtual Environment and Dependencies

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install PyQt5 openai-whisper sounddevice wavio pyperclip soundfile scipy
```

### 3. Launch Application

You can run either the system tray version or the windowed version:

```bash
# System tray version
python windows_whisper_app.py

# Windowed version (recommended for better UI)
python windows_whisper_app_fixed.py
```

## Usage Guide

### Windowed Interface

The application provides a user-friendly windowed interface with:

1. **Recording Controls**
   - Start/Stop recording buttons
   - Recording timer display
   - Status indicator

2. **Model Selection**
   - Choose between different Whisper models:
     - tiny: Fastest, least accurate
     - base: Good balance of speed and accuracy
     - small: Better accuracy, slower
     - medium: Best accuracy, slowest

3. **Transcription History**
   - View history of recent transcriptions
   - Each transcription includes timestamp

4. **Settings**
   - Auto-copy to clipboard option

### Features

1. **Recording**
   - Click "Start Recording" button
   - Speak into microphone
   - Click "Stop Recording" when done

2. **Transcription**
   - Automatic processing after recording stops
   - Results window appears with transcribed text
   - Option to copy to clipboard
   - History of recent transcriptions maintained

## Technical Implementation Details

### Audio Recording and Processing

1. **Recording**:
   - Uses `sounddevice` to capture audio at 16kHz (Whisper's expected sample rate)
   - Stores audio data in a queue to prevent buffer overflows
   - Processes audio data as NumPy arrays

2. **Audio Processing**:
   - Converts audio to float32 format required by Whisper
   - Normalizes audio levels for better transcription
   - Handles mono/stereo conversion

3. **Transcription**:
   - Processes audio directly with Whisper model
   - Runs transcription in a separate thread to keep UI responsive
   - Communicates results back to main thread using Qt signals

### Troubleshooting

1. **Installation Problems**
   - Verify Python 3.11+ is installed: `python --version`
   - Ensure all dependencies are installed: `pip list`

2. **Audio Recording Issues**
   - Grant microphone permissions in Windows Settings
   - Check audio input device in Windows Sound settings
   - Try running with administrator privileges

3. **Transcription Issues**
   - For memory errors, try using a smaller model (tiny or base)
   - Ensure speech is clear and microphone is working properly
   - Check the log file for detailed error information

## License

MIT License - See LICENSE file for details
