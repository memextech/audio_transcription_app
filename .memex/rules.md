# Audio Transcriber - Cross-Platform Technical Overview & Setup Guide

This project provides instant audio transcription using Whisper, with platform-specific implementations for macOS (using Whisper MLX) and Windows (using OpenAI Whisper).

## Platform-Specific Implementations

### macOS Version
- Native menu bar application optimized for Apple Silicon
- Uses Whisper MLX for fast transcription
- Integrates with macOS menu bar using rumps

### Windows Version
- Available as both system tray and windowed application
- Uses standard OpenAI Whisper for transcription
- Built with PyQt5 for cross-platform GUI support

## Installation Steps

### macOS Installation

#### 1. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Install uv package manager if not present
2. Create Python virtual environment
3. Install dependencies
4. Generate app icon
5. Create app bundle

#### 2. Launch Application
```bash
open "Audio Transcriber.app"
```

### Windows Installation

#### 1. Install Python
If you don't have Python installed:
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, make sure to check "Add Python to PATH"

#### 2. Setup Virtual Environment and Dependencies
```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install PyQt5 openai-whisper sounddevice wavio pyperclip soundfile scipy
```

#### 3. Launch Application
You can run either the system tray version or the windowed version:
```bash
# System tray version
python windows_whisper_app.py

# Windowed version (recommended for better UI)
python windows_whisper_app_fixed.py
```

## Usage Guide

### macOS: Menu Bar Interface
- Ready to record
- Recording in progress
- Transcribing
- Transcription complete

#### Features
1. **Recording**
   - Click menu bar icon
   - Select "Start Recording"
   - Speak into microphone
   - Click "Stop Recording"

2. **Transcription**
   - Automatic processing
   - Results window
   - Clipboard copy
   - History storage

### Windows: Application Interface

#### System Tray Version
- Right-click the system tray icon to access menu options
- Similar workflow to macOS version

#### Windowed Version (Recommended)
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

## Troubleshooting

### macOS Common Issues

1. **Installation Problems**
   - Verify Python 3.11+ is installed
   - Check uv installation: `uv --version`
   - Ensure all paths in setup.sh are accessible

2. **App Won't Launch or Menu Bar Icon Missing**
   - Check virtual environment: `.venv/bin/python --version`
   - Verify app bundle structure
   - Check process is running: `ps aux | grep menubar_app.py`
   - Check system logs: Open Console.app and filter for "AudioTranscriber"
   - Check menu bar settings in System Preferences > Control Center
   - If app runs from terminal but not from click:
     ```bash
     # Run these commands to rebuild with proper permissions
     rm -rf "Audio Transcriber.app"
     ./create_app.sh
     ```
   - Key requirements for proper app bundle:
     - Correct Info.plist with LSUIElement set to true
     - Properly activated virtual environment in launcher script
     - Correct working directory set in launcher script
     - Proper code signing (even if self-signed)

3. **Recording Issues**
   - Grant microphone permissions
   - Check audio input device
   - Verify sounddevice installation

4. **Launcher Script Issues**
   - The launcher script must:
     - Set proper PATH including Homebrew paths
     - Activate virtual environment using source
     - Change to correct working directory
     - Use absolute paths for Python and app script
     - Include logging for troubleshooting
   Example launcher script structure:
   ```bash
   #!/bin/bash
   function log_msg() {
       /usr/bin/logger -t "AudioTranscriber" "$1"
   }
   export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
   export APP_DIR="/path/to/app"
   cd "$APP_DIR"
   source "$APP_DIR/.venv/bin/activate"
   exec "$APP_DIR/.venv/bin/python" "$APP_DIR/menubar_app.py"
   ```

### Windows Common Issues

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

4. **Audio Processing Issues**
   - If you encounter FFmpeg-related errors, the app is designed to work without it
   - The app uses direct audio processing with soundfile and scipy
   - Check that audio format conversion is working properly

## Development

For further development of the app, here is an overview of the repo:

```
audio_transcription_app/
├── menubar_app.py          # Main application logic (macOS)
├── windows_whisper_app.py  # System tray application (Windows)
├── windows_whisper_app_fixed.py # Windowed application (Windows)
├── create_icon.py          # Icon generation script (macOS)
├── create_app.sh           # App bundle creation script (macOS)
├── setup.sh                # Environment and app setup script (macOS)
├── setup_windows.py        # Setup script for Windows
├── requirements.txt        # Python dependencies (macOS)
├── .memex/rules.md         # This guide
├── README_WINDOWS.md       # Windows-specific documentation
├── assets/                 # Application assets
│   ├── audio_transcriber_icon.png  # Source icon
│   └── AppIcon.icns        # MacOS app icon - will be generated
└── Audio Transcriber.app/  # Application bundle - will be generated (macOS only)
```

### Project Configuration

#### macOS Configuration

All paths in the application are relative to the project directory. Key files:

- `create_icon.py`: Handles icon generation
  - Input: assets/audio_transcriber_icon.png
  - Output: assets/AppIcon.icns

- `create_app.sh`: Creates app bundle
  - Uses project directory for paths
  - Generates launcher script with correct virtual environment path

- `setup.sh`: Manages environment setup
  - Installs dependencies
  - Runs icon generation
  - Creates app bundle

#### Windows Configuration

- `windows_whisper_app.py`: System tray application
  - Uses PyQt5 for system tray integration
  - Similar workflow to macOS version

- `windows_whisper_app_fixed.py`: Windowed application
  - More user-friendly interface
  - Direct audio processing without FFmpeg
  - Model selection and other settings

- `setup_windows.py`: Setup script for Windows
  - Creates virtual environment
  - Installs dependencies

## Technology Stack

### macOS Core Components
- **Whisper MLX**: Apple's MLX-based Whisper implementation
- **Python 3.11+**: Core runtime
- **rumps**: macOS menu bar integration
- **sounddevice + wavio**: Audio capture
- **uv**: Python package management

### macOS System Requirements
- macOS 11.0 or later
- Apple Silicon Mac (M1/M2/M3)
- Microphone permissions

### Windows Core Components
- **OpenAI Whisper**: Standard Whisper implementation
- **Python 3.11+**: Core runtime
- **PyQt5**: GUI framework for system tray and windowed interface
- **sounddevice + wavio**: Audio capture
- **soundfile + scipy**: Audio processing without FFmpeg
- **pyperclip**: Clipboard integration

### Windows System Requirements
- Windows 10 or later
- Python 3.11 or later
- Microphone permissions

## License
MIT License - See LICENSE file for details
