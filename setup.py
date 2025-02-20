from setuptools import setup

APP = ['menubar_app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icons/AppIcon.icns',
    'plist': {
        'LSUIElement': True,  # Makes it a menu bar app
        'CFBundleName': 'Audio Transcriber',
        'CFBundleDisplayName': 'Audio Transcriber',
        'CFBundleIdentifier': 'com.audiotranscriber.app',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'LSMinimumSystemVersion': '11.0',
        'NSMicrophoneUsageDescription': 'Audio Transcriber needs access to your microphone to record audio for transcription.',
        'NSAppleEventsUsageDescription': 'Audio Transcriber needs to control system events for recording.',
    },
    'packages': [
        'rumps',
        'sounddevice',
        'numpy',
        'wavio',
        'lightning_whisper_mlx',
        'pyperclip',
        'PIL',
    ],
}

setup(
    name='Audio Transcriber',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
