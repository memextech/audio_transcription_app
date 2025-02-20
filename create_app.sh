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

# Create launcher script
cat > "$APP_PATH/Contents/MacOS/AudioTranscriber" << EOL
#!/bin/bash
SCRIPT_DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="\$(dirname "\$(dirname "\$(dirname "\$SCRIPT_DIR")")")"

# Activate virtual environment and run app
source "\$PROJECT_DIR/.venv/bin/activate"
exec python3 "\$PROJECT_DIR/menubar_app.py"
EOL

# Make launcher executable
chmod +x "$APP_PATH/Contents/MacOS/AudioTranscriber"

echo "App bundle created at: $APP_PATH"
