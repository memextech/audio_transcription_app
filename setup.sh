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

# Create virtual environment with Python 3.11
echo "Creating virtual environment..."
cd "$SCRIPT_DIR"
uv venv --python 3.11

# Activate virtual environment and set Python path
source .venv/bin/activate
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Generate app icon
echo "Generating app icon..."
"$VENV_PYTHON" create_icon.py

# Download the model
echo "Downloading Whisper MLX model..."
"$VENV_PYTHON" download_model.py

# Create app bundle
echo "Creating app bundle..."
bash create_app.sh

echo "Setup complete! You can now run the app using:"
echo "open '$SCRIPT_DIR/Audio Transcriber.app'"
