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
├── running.md            # This guide
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

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/audio_transcription_app_setup.git
cd audio_transcription_app_setup
```

### 2. Run Setup Script
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

1. Install uv:
```bash
# Via homebrew
brew install uv
# Or via curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment:
```bash
uv venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Generate icon:
```bash
python3 create_icon.py
```

5. Create app bundle:
```bash
./create_app.sh
```

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

2. **App Won't Launch**
   - Check virtual environment: `.venv/bin/python --version`
   - Verify app bundle structure
   - Check Console.app for logs

3. **Recording Issues**
   - Grant microphone permissions
   - Check audio input device
   - Verify sounddevice installation

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

### Adding Dependencies
1. Add to requirements.txt
2. Install in virtual environment:
```bash
uv pip install -r requirements.txt
```

## Contributing

### Setup Development Environment
1. Fork repository
2. Clone locally
3. Run setup.sh
4. Create feature branch
5. Make changes
6. Submit pull request

### Guidelines
- Follow PEP 8
- Add tests for new features
- Update documentation
- Keep commits atomic

## License
MIT License - See LICENSE file for details
