# Audio Transcription App

This templates develops and spins up a native macOS menu bar application for real-time audio transcription using Whisper MLX, optimized for Apple Silicon.

## Features

- 🎙️ One-click audio recording from menu bar
- ⚡ Fast transcription using Whisper MLX
- 📋 Automatic clipboard copy
- 🔄 Transcription history
- 🎯 Native macOS integration

## Potential app functionality expansions to explore

Here are some ideas of how to expand this template after you get it up and running:
- Create a library of generated transcripts
- Functionality to save transcripts as .txt files
- LLM connection to generate transcript summaries

## Requirements

- macOS 11.0 or later
- Apple Silicon Mac (M1/M2/M3)
- Python 3.11+
- Microphone permissions

## Quick Start

Just ask Memex to run this app locally and it will take care of the rest! If you run into any errors, just point Memex to fix them.

If you’d like to set up the environment and dependencies manually, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/memextech/audio_transcription_app.git
cd audio_transcription_app
```

2. Run setup script:
```bash
chmod +x setup.sh
./setup.sh
```

3. Launch the app:
```bash
open "Audio Transcriber.app"
```

## Development

See Rules for AI (rendered from `.memex/rules.md`) for detailed development guidelines Memex will follow, including:
- Complete setup instructions
- Model-specific parameters
- Error handling
- Potential improvements
- Development workflow

You can ask Memex to update rules.md to reflect your project needs as you expand it, or set it as part of your Custom Instructions so that it does it automatically after important steps.


## License

MIT License
