# Audio Transcriber - Technical Overview & Setup Guide

A native macOS menu bar application that provides instant audio transcription using Whisper MLX, optimized for Apple Silicon.

## Repository Structure

```
audio_transcription_app_setup/
├── menubar_app.py          # Main application logic
├── create_icon.py          # Icon generation script
├── create_app.sh           # App bundle creation script
├── setup.sh               # Environment and app setup script
├── requirements.txt       # Python dependencies
├── .memex/rules.md            # This guide
├── assets/               # Application assets
│   ├── audio_transcriber_icon.png  # Source icon
│   └── AppIcon.icns      # Generated macOS app icon
└── Audio Transcriber.app/  # Generated application bundle
```

## Technology Stack

### Core Components
- **Whisper MLX**: Apple's MLX-based Whisper implementation
- **Python 3.11+**: Core runtime
- **rumps**: macOS menu bar integration
- **sounddevice + wavio**: Audio capture
- **uv**: Python package management

### System Requirements
- macOS 11.0 or later
- Apple Silicon Mac (M1/M2/M3)
- Microphone permissions

## Installation Steps

### 1. Run Setup Script
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

### 3. Launch Application
```bash
open "Audio Transcriber.app"
```

## Development Environment

### Manual Setup
If you prefer to set up manually:

1. Create virtual environment:
```bash
cd /path/to/project
uv venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

3. Download Whisper MLX model:
```bash
.venv/bin/python download_model.py
```

4. Generate icon:
```bash
.venv/bin/python create_icon.py
```

5. Create app bundle:
```bash
./create_app.sh
```

Note: Always use the virtual environment's Python interpreter (.venv/bin/python) to ensure consistent dependencies.

### Project Configuration

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

## Usage Guide

### Menu Bar Interface
- 🎙️ Ready to record
- ⏹️ Recording in progress
- ⏳ Transcribing
- ✨ Transcription complete

### Features
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

## Troubleshooting

### Common Issues

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

## Development

### Making Changes
1. Activate virtual environment:
```bash
source .venv/bin/activate
```

2. Edit source files
3. Rebuild app bundle:
```bash
./create_app.sh
```

## License
MIT License - See LICENSE file for details
