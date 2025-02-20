#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    if command -v brew &> /dev/null; then
        brew install uv
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
fi

# Create virtual environment
echo "Creating virtual environment..."
cd "$SCRIPT_DIR"
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Generate app icon
echo "Generating app icon..."
python3 create_icon.py

# Create app bundle
echo "Creating app bundle..."
bash create_app.sh

echo "Setup complete! You can now run the app using:"
echo "open '$SCRIPT_DIR/Audio Transcriber.app'"
