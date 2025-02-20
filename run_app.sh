#!/bin/bash
APP_DIR="/Users/chilang/Workspace/audio_transcription_app_setup"
cd "$APP_DIR"
source "$APP_DIR/.venv/bin/activate"
exec "$APP_DIR/.venv/bin/python" "$APP_DIR/menubar_app.py"
