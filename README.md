# Audio Transcription App

A native macOS menu bar application for real-time audio transcription using MLX-Whisper, optimized for Apple Silicon.

## Features

- 🎙️ One-click audio recording from menu bar
- ⚡ Fast transcription using MLX-Whisper
- 📋 Automatic clipboard copy
- 🔄 Transcription history
- 🎯 Native macOS integration

## What's New

This version uses the official `mlx-whisper` package from Apple's ML Explore team instead of `lightning-whisper-mlx`, providing:
- Better compatibility with the latest macOS versions
- Access to Hugging Face's model repository
- More stable performance on Apple Silicon
- Simplified dependency management

## Requirements

- macOS 11.0 or later
- Apple Silicon Mac (M1/M2/M3)
- Python 3.11+
- Microphone permissions
- Internet connection (for first-time model download)

## Installation

### Quick Setup (Recommended)
Run the setup script to automatically install dependencies, build the app, and copy it to your Applications folder:

```bash
chmod +x setup.sh
./setup.sh
```

### Manual Installation
If you prefer to install manually:

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install mlx mlx-whisper rumps sounddevice wavio pyperclip pillow tqdm
   ```

3. Generate the app icon:
   ```bash
   python create_icon.py
   ```

4. Download the model (optional - will download on first use):
   ```bash
   python download_model.py
   ```

5. Create the app bundle:
   ```bash
   bash create_app.sh
   ```

6. Copy to Applications (optional):
   ```bash
   cp -R "Audio Transcriber.app" /Applications/
   ```

## Usage

### Starting the App
Launch the app from:
- Finder: `/Applications/Audio Transcriber.app` 
- Spotlight: Search for "Audio Transcriber"
- Terminal: `open "/Applications/Audio Transcriber.app"`

The app will appear as a 🎙️ icon in your menu bar.

### Recording and Transcribing
1. Click on the 🎙️ icon in your menu bar
2. Select "Start Recording" 
3. Speak into your microphone
4. Click on the menu again and select "Stop Recording"
5. Wait for the transcription to complete (the icon will change to indicate progress)
6. The transcribed text will appear in a window
7. Click "Copy & Close" to copy the text to your clipboard

### Additional Features
- **Transcription History**: Access previous transcriptions from the "Recent Transcriptions" menu
- **Auto-Copy**: Toggle automatic copying to clipboard in the Settings menu

## Technical Details

This application uses:
- `mlx-whisper`: Apple Silicon optimized version of OpenAI's Whisper
- `rumps`: for macOS menu bar integration
- Hugging Face model: `mlx-community/whisper-medium-mlx`
- The model is automatically downloaded on first use

The app creates log files in the `logs` directory within the project folder for troubleshooting.

## Troubleshooting

If you encounter issues:
- Check the logs in `logs/app.log`
- Ensure your microphone permissions are enabled in System Preferences -> Privacy & Security -> Microphone
- Try restarting the app
- Verify that all dependencies are installed correctly

### Common Issues
1. **App Won't Launch**: Check that the app bundle is properly signed and has the correct permissions
2. **No Menu Bar Icon**: Ensure the app is running (`ps aux | grep menubar_app.py`)
3. **Transcription Errors**: Could indicate issues with the Whisper model - check logs for details

## Uninstalling
To uninstall:
1. Remove the app from Applications folder:
   ```bash
   rm -rf "/Applications/Audio Transcriber.app"
   ```
2. Remove the project directory if desired

## Development

For detailed development guidelines, see the `.memex/rules.md` file, which includes:
- Complete setup instructions
- Architecture overview
- Troubleshooting guidance
- Development workflow

## License

MIT License
