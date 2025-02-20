# Audio Transcription Menu Bar App Setup Guide

This guide provides step-by-step instructions for creating a macOS menu bar application that performs real-time audio transcription using Whisper MLX.

## Project Structure

```
audio_transcription_app_setup/
├── menubar_app.py          # Main application code
├── create_icon.py          # Icon generation script
├── create_app.sh           # App bundle creation script
├── run_app.sh             # Development launch script
├── requirements.txt       # Python dependencies
└── icons/                # Generated app icons
    └── AppIcon.icns      # macOS app icon
```

## Setup Instructions

### 1. Environment Setup

```bash
# Create project directory
mkdir audio_transcription_app_setup
cd audio_transcription_app_setup

# Create Python virtual environment using uv
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install lightning-whisper-mlx rumps sounddevice numpy wavio pyperclip pillow
```

### 2. Create Application Files

#### menubar_app.py
```python
import rumps
import sounddevice as sd
import numpy as np
import wavio
import tempfile
import os
import time
from lightning_whisper_mlx import LightningWhisperMLX
import threading
import queue
import pyperclip
from datetime import datetime

class TranscriptionWindow(rumps.Window):
    def __init__(self, title, message, dimensions=(500, 300)):
        # Create a window with a text field instead of just a message
        super(TranscriptionWindow, self).__init__(
            title=title,
            message="",  # Empty message as we'll use a text field
            dimensions=dimensions,
            ok="Copy & Close",
            cancel=None  # Remove the second button to simplify
        )
        # Set the default text in the main text field
        self.default_text = message
        
    def run(self):
        # Override run to set the text field content
        self._textfield.setStringValue_(self.default_text)
        self._textfield.setEditable_(True)  # Make the text editable
        self._textfield.setSelectable_(True)  # Make the text selectable
        return super(TranscriptionWindow, self).run()

class AudioTranscriptionApp(rumps.App):
    def __init__(self):
        super(AudioTranscriptionApp, self).__init__(
            name="Audio Transcriber",
            title="🎙️",
            quit_button=None  # Custom quit button
        )
        
        # Initialize Whisper model
        self.whisper_model = LightningWhisperMLX(model="distil-medium.en", batch_size=12, quant=None)
        
        # Recording state
        self.recording = False
        self.audio_data = []
        self.audio_queue = queue.Queue()
        self.sample_rate = 44100
        self.start_time = None
        self.transcription_history = []
        
        # Menu items
        self.start_button = rumps.MenuItem(
            title="Start Recording",
            callback=self.start_recording
        )
        self.stop_button = rumps.MenuItem(
            title="Stop Recording",
            callback=self.stop_recording
        )
        self.stop_button.set_callback(None)  # Disable initially
        
        self.timer_item = rumps.MenuItem(title="00:00")
        self.timer_item.set_callback(None)  # Make it non-clickable
        
        self.status_item = rumps.MenuItem(title="Ready to record")
        self.status_item.set_callback(None)
        
        # History submenu
        self.history_menu = rumps.MenuItem("Recent Transcriptions")
        no_history = rumps.MenuItem("No recent transcriptions")
        no_history.set_callback(None)
        self.history_menu.add(no_history)
        
        # Settings submenu
        self.settings_menu = rumps.MenuItem("Settings")
        self.auto_copy = rumps.MenuItem("Auto-copy to clipboard", 
                                      callback=self.toggle_auto_copy)
        self.auto_copy.state = True  # Enable by default
        self.settings_menu.add(self.auto_copy)
        
        # Add menu items
        self.menu = [
            self.start_button,
            self.stop_button,
            None,  # Separator
            self.status_item,
            self.timer_item,
            None,  # Separator
            self.history_menu,
            None,  # Separator
            self.settings_menu,
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]
        
        self.transcribed_text = None
    
    def update_history_menu(self):
        # Remove all existing items
        if len(self.history_menu._menu.itemArray()):
            for _ in range(len(self.history_menu._menu.itemArray())):
                self.history_menu._menu.removeItemAtIndex_(0)
        
        if not self.transcription_history:
            no_history = rumps.MenuItem("No recent transcriptions")
            no_history.set_callback(None)
            self.history_menu.add(no_history)
        else:
            # Add recent transcriptions (last 5)
            for timestamp, text in self.transcription_history[-5:]:
                # Create a preview (first 30 chars)
                preview = text[:30] + "..." if len(text) > 30 else text
                menu_item = rumps.MenuItem(
                    f"{timestamp.strftime('%H:%M:%S')}: {preview}",
                    callback=lambda x, t=text: self.show_transcription_from_history(t)
                )
                self.history_menu.add(menu_item)
            
            # Add clear history option
            self.history_menu.add(None)  # Separator
            self.history_menu.add(
                rumps.MenuItem("Clear History", callback=self.clear_history)
            )
    
    def clear_history(self, _):
        self.transcription_history = []
        self.update_history_menu()
    
    def show_transcription_from_history(self, text):
        self.show_transcription_window(text)
    
    def toggle_auto_copy(self, sender):
        sender.state = not sender.state
    
    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(status)
        self.audio_queue.put(indata.copy())
    
    def update_timer(self):
        while self.recording:
            elapsed = time.time() - self.start_time
            mins, secs = divmod(int(elapsed), 60)
            self.timer_item.title = f"⏱️ {mins:02d}:{secs:02d}"
            time.sleep(0.1)
    
    def start_recording(self, _):
        self.recording = True
        self.audio_data = []
        self.start_time = time.time()
        
        # Update UI
        self.start_button.set_callback(None)  # Disable start button
        self.stop_button.set_callback(self.stop_recording)  # Enable stop button
        self.title = "⏹️"  # Change menu bar icon to stop icon
        self.status_item.title = "Recording in progress..."
        self.start_button.title = "Recording..."
        
        # Start audio stream
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            callback=self.audio_callback
        )
        self.stream.start()
        
        # Start timer update thread
        threading.Thread(target=self.update_timer, daemon=True).start()
    
    def stop_recording(self, _):
        if not self.recording:
            return
            
        self.recording = False
        self.status_item.title = "Processing audio..."
        
        # Stop the stream
        self.stream.stop()
        self.stream.close()
        
        # Process all remaining audio in queue
        while not self.audio_queue.empty():
            self.audio_data.extend(self.audio_queue.get()[:, 0])
        
        # Convert to numpy array
        recording = np.array(self.audio_data)
        
        if len(recording) > 0:
            # Save the recording to a temporary WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                wavio.write(temp_audio.name, recording, self.sample_rate, sampwidth=2)
                
                # Update UI to show transcribing status
                self.title = "⏳"
                self.status_item.title = "Transcribing..."
                
                # Transcribe the audio
                result = self.whisper_model.transcribe(audio_path=temp_audio.name)
                self.transcribed_text = result['text']
                
                # Add to history
                self.transcription_history.append((datetime.now(), self.transcribed_text))
                self.update_history_menu()
                
                # Auto-copy if enabled
                if self.auto_copy.state:
                    pyperclip.copy(self.transcribed_text)
                    self.status_item.title = "Transcription copied to clipboard!"
                
                # Show transcription window
                self.show_transcription_window(self.transcribed_text)
                
                # Clean up
                os.unlink(temp_audio.name)
        
        # Reset UI
        self.title = "🎙️"
        self.timer_item.title = "00:00"
        self.status_item.title = "Ready to record"
        self.start_button.title = "Start Recording"
        self.start_button.set_callback(self.start_recording)  # Enable start button
        self.stop_button.set_callback(None)  # Disable stop button
    
    def show_transcription_window(self, text):
        window = TranscriptionWindow(
            title="✨ Transcription",
            message=text
        )
        response = window.run()
        
        # Copy to clipboard when user clicks "Copy & Close"
        if response.clicked:
            pyperclip.copy(text)
            self.status_item.title = "Transcription copied to clipboard!"
    
    def quit_app(self, _):
        rumps.quit_application()

if __name__ == "__main__":
    AudioTranscriptionApp().run()

```

#### create_icon.py
```python
# Full content of create_icon.py as in the repository
```

#### create_app.sh
```bash
#!/bin/bash

# Create the application bundle structure
rm -rf "Audio Transcriber.app"
mkdir -p "Audio Transcriber.app/Contents/MacOS"
mkdir -p "Audio Transcriber.app/Contents/Resources"

# Create the launcher script that includes error logging
cat > "Audio Transcriber.app/Contents/MacOS/AudioTranscriber" << 'EOF'
#!/bin/bash

# Log to system log with identifier
function log_msg() {
    /usr/bin/logger -t "AudioTranscriber" "$1"
}

log_msg "Starting Audio Transcription application"

# Environment setup
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
export APP_DIR="/Users/chilang/Workspace/audio_transcription_app_setup"

log_msg "Changing to app directory: $APP_DIR"
cd "$APP_DIR"

log_msg "Activating virtual environment"
source "$APP_DIR/.venv/bin/activate"

log_msg "Launching Python application"
exec "$APP_DIR/.venv/bin/python" "$APP_DIR/menubar_app.py"
EOF

# Create the Info.plist file
cat > "Audio Transcriber.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>AudioTranscriber</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.audiotranscriber.app</string>
    <key>CFBundleName</key>
    <string>AudioTranscriber</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Make scripts executable
chmod +x "Audio Transcriber.app/Contents/MacOS/AudioTranscriber"

# Copy the icon if it exists
if [ -f "icons/AppIcon.icns" ]; then
    cp icons/AppIcon.icns "Audio Transcriber.app/Contents/Resources/"
fi

echo "App bundle created. Check Console.app for 'AudioTranscriber' messages."
```

#### run_app.sh
```bash
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python menubar_app.py
```

### 3. Make Scripts Executable

```bash
chmod +x create_app.sh run_app.sh
```

### 4. Generate App Icon

1. Place your source icon at `~/Downloads/audio_transcriber_icon.png`
2. Run the icon generation script:
```bash
python create_icon.py
```

### 5. Build the App Bundle

```bash
./create_app.sh
```

### 6. Testing

#### Development Mode
```bash
./run_app.sh
```

#### Production Mode
```bash
open "Audio Transcriber.app"
```

## Application Features

1. **Menu Bar Integration**
   - Lives in the macOS menu bar
   - Shows recording status via icon changes
   - Provides easy access to controls

2. **Audio Recording**
   - One-click recording start/stop
   - Visual feedback during recording
   - Timer display

3. **Transcription**
   - Uses Whisper MLX for fast transcription
   - Optimized for Apple Silicon
   - Automatic clipboard integration

4. **History Management**
   - Keeps track of recent transcriptions
   - Easy access to past transcriptions
   - Clear history option

5. **Settings**
   - Auto-copy to clipboard toggle
   - More settings can be added easily

## Troubleshooting

1. **App Won't Launch**
   - Check Console.app for "AudioTranscriber" messages
   - Verify virtual environment path in launch script
   - Check Python dependencies

2. **Recording Issues**
   - Verify microphone permissions
   - Check sounddevice configuration
   - Monitor system audio input settings

3. **Icon Issues**
   - Regenerate icon using create_icon.py
   - Verify icon file exists and is readable
   - Check app bundle structure

## Development Notes

1. **Path Configuration**
   - Update APP_DIR in create_app.sh to match your setup
   - Adjust virtual environment path if needed
   - Verify all paths in launch scripts

2. **Dependencies**
   - All Python packages should be installed in the virtual environment
   - System dependencies (like PortAudio) should be installed globally
   - Use uv for package management

3. **Logging**
   - App logs to system log with identifier "AudioTranscriber"
   - View logs in Console.app or using `log show` command
   - Additional logging can be added as needed

## Security Notes

1. **Microphone Access**
   - App requires microphone permissions
   - macOS will prompt for access on first run
   - Can be managed in System Preferences > Security & Privacy

2. **File System Access**
   - App needs access to its directory and virtual environment
   - Temporary files are created for audio processing
   - Cleanup is handled automatically

## Future Improvements

1. **Keyboard Shortcuts**
   - Add global shortcuts for start/stop recording
   - Implement shortcut customization

2. **Transcription Options**
   - Add language selection
   - Implement different Whisper models
   - Add transcription formatting options

3. **UI Enhancements**
   - Add progress indicators
   - Implement dark mode support
   - Add more visual feedback

## References

- [Whisper MLX Documentation](https://github.com/ml-explore/mlx-examples/tree/main/whisper)
- [Rumps Documentation](https://github.com/jaredks/rumps)
- [macOS App Bundle Structure](https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/BundleTypes/BundleTypes.html)
