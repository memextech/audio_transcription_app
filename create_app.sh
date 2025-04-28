#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_NAME="Audio Transcriber.app"
APP_PATH="$SCRIPT_DIR/$APP_NAME"

# Create app bundle structure
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Generate icon if it doesn't exist
if [ ! -f "$SCRIPT_DIR/assets/AppIcon.icns" ]; then
    echo "Generating app icon..."
    python3 "$SCRIPT_DIR/create_icon.py"
fi

# Copy icon
cp "$SCRIPT_DIR/assets/AppIcon.icns" "$APP_PATH/Contents/Resources/"

# Create Info.plist
cat > "$APP_PATH/Contents/Info.plist" << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>AudioTranscriber</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.example.audiotranscriber</string>
    <key>CFBundleName</key>
    <string>Audio Transcriber</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
EOL

# Create Info.plist
cat > "$APP_PATH/Contents/Info.plist" << EOL
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
EOL

# Create launcher script with logging and proper environment setup
cat > "$APP_PATH/Contents/MacOS/AudioTranscriber" << EOL
#!/bin/bash

# Log to system log with identifier
function log_msg() {
    /usr/bin/logger -t "AudioTranscriber" "\$1"
}

log_msg "Starting Audio Transcriber application"

# Environment setup
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:\$PATH"
export APP_DIR="$SCRIPT_DIR"

log_msg "Changing to app directory: \$APP_DIR"
cd "\$APP_DIR"

log_msg "Activating virtual environment"
source "\$APP_DIR/.venv/bin/activate"

log_msg "Launching Python application"

# Set PATH to include Homebrew paths
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"

# Set PYTHONPATH to ensure all modules can be found
export PYTHONPATH="\$APP_DIR:\$PYTHONPATH"

# Create log directory
mkdir -p "\$APP_DIR/logs"

# Run the app
exec "\$APP_DIR/.venv/bin/python" "\$APP_DIR/menubar_app.py" >> "\$APP_DIR/logs/app.log" 2>&1
EOL

# Make launcher executable
chmod +x "$APP_PATH/Contents/MacOS/AudioTranscriber"

# Sign the app with ad-hoc signature (development only)
codesign --force --deep --sign - "$APP_PATH"

# Remove quarantine attribute if present
xattr -d com.apple.quarantine "$APP_PATH" 2>/dev/null || true

echo "App bundle created and signed at: $APP_PATH"
