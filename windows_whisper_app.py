import sys
import os
import time
import tempfile
import threading
import queue
from datetime import datetime
import numpy as np
import sounddevice as sd
import wavio
import pyperclip
import whisper
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QAction, 
                            QDialog, QVBoxLayout, QTextEdit, QPushButton,
                            QHBoxLayout, QLabel, QComboBox)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject

class TranscriptionSignals(QObject):
    """Signal class for thread communication"""
    finished = pyqtSignal(str)
    status_update = pyqtSignal(str)

class TranscriptionWindow(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✨ Transcription")
        self.setMinimumSize(500, 300)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create text edit for transcription
        self.text_edit = QTextEdit()
        self.text_edit.setText(text)
        self.text_edit.setReadOnly(False)
        font = QFont()
        font.setPointSize(11)
        self.text_edit.setFont(font)
        layout.addWidget(self.text_edit)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Copy button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def copy_to_clipboard(self):
        text = self.text_edit.toPlainText()
        pyperclip.copy(text)

class AudioTranscriptionApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Initialize tray icon
        self.tray_icon = QSystemTrayIcon()
        icon_path = os.path.join("assets", "audio_transcriber_icon.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Use a default icon from PyQt if the custom icon is not available
            self.tray_icon.setIcon(self.app.style().standardIcon(QApplication.style().SP_MediaPlay))
        
        self.tray_icon.setToolTip("Audio Transcriber")
        
        # Initialize Whisper model
        self.signals = TranscriptionSignals()
        self.signals.status_update.connect(self.update_status)
        self.signals.finished.connect(self.transcription_finished)
        
        # Recording state
        self.recording = False
        self.audio_data = []
        self.audio_queue = queue.Queue()
        self.sample_rate = 16000  # Whisper expects 16kHz audio
        self.start_time = None
        self.transcription_history = []
        self.transcribed_text = None
        self.current_model = "base"  # Default model
        
        # Create menu
        self.menu = QMenu()
        
        # Status item
        self.status_action = QAction("Ready to record")
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)
        
        # Timer item
        self.timer_action = QAction("00:00")
        self.timer_action.setEnabled(False)
        self.menu.addAction(self.timer_action)
        self.menu.addSeparator()
        
        # Start recording action
        self.start_action = QAction("Start Recording")
        self.start_action.triggered.connect(self.start_recording)
        self.menu.addAction(self.start_action)
        
        # Stop recording action
        self.stop_action = QAction("Stop Recording")
        self.stop_action.triggered.connect(self.stop_recording)
        self.stop_action.setEnabled(False)
        self.menu.addAction(self.stop_action)
        self.menu.addSeparator()
        
        # History submenu
        self.history_menu = self.menu.addMenu("Recent Transcriptions")
        self.update_history_menu()
        self.menu.addSeparator()
        
        # Settings submenu
        self.settings_menu = self.menu.addMenu("Settings")
        self.auto_copy_action = QAction("Auto-copy to clipboard")
        self.auto_copy_action.setCheckable(True)
        self.auto_copy_action.setChecked(True)
        self.settings_menu.addAction(self.auto_copy_action)
        
        # Model selection submenu
        self.model_menu = self.settings_menu.addMenu("Model")
        self.model_actions = {}
        for model_name in ["tiny", "base", "small", "medium"]:  # Excluding "large" as it's resource-intensive
            action = QAction(model_name)
            action.setCheckable(True)
            if model_name == self.current_model:
                action.setChecked(True)
            action.triggered.connect(lambda checked, m=model_name: self.change_model(m))
            self.model_menu.addAction(action)
            self.model_actions[model_name] = action
        
        self.menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(quit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(self.menu)
        
        # Timer for updating recording time
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # Initialize the model
        self.load_model()
    
    def load_model(self):
        try:
            self.status_action.setText(f"Loading {self.current_model} model...")
            self.whisper_model = whisper.load_model(self.current_model)
            self.status_action.setText("Ready to record")
        except Exception as e:
            self.status_action.setText(f"Error loading model: {str(e)}")
    
    def change_model(self, model_name):
        # Update checkmarks
        for name, action in self.model_actions.items():
            action.setChecked(name == model_name)
        
        self.current_model = model_name
        
        # Load the new model
        self.load_model()
    
    def update_history_menu(self):
        # Clear the history menu
        self.history_menu.clear()
        
        if not self.transcription_history:
            no_history = QAction("No recent transcriptions")
            no_history.setEnabled(False)
            self.history_menu.addAction(no_history)
        else:
            # Add recent transcriptions (last 5)
            for timestamp, text in self.transcription_history[-5:]:
                # Create a preview (first 30 chars)
                preview = text[:30] + "..." if len(text) > 30 else text
                menu_item = QAction(f"{timestamp.strftime('%H:%M:%S')}: {preview}")
                # Use a lambda with default argument to capture the current text
                menu_item.triggered.connect(lambda checked, t=text: self.show_transcription_window(t))
                self.history_menu.addAction(menu_item)
            
            # Add clear history option
            self.history_menu.addSeparator()
            clear_action = QAction("Clear History")
            clear_action.triggered.connect(self.clear_history)
            self.history_menu.addAction(clear_action)
    
    def clear_history(self):
        self.transcription_history = []
        self.update_history_menu()
    
    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(status)
        self.audio_queue.put(indata.copy())
    
    def update_timer(self):
        if self.recording and self.start_time:
            elapsed = time.time() - self.start_time
            mins, secs = divmod(int(elapsed), 60)
            self.timer_action.setText(f"⏱️ {mins:02d}:{secs:02d}")
    
    def update_status(self, message):
        self.status_action.setText(message)
    
    def start_recording(self):
        self.recording = True
        self.audio_data = []
        self.start_time = time.time()
        
        # Update UI
        self.start_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.tray_icon.setToolTip("⏹️ Recording...")
        self.status_action.setText("Recording in progress...")
        
        # Start audio stream
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            callback=self.audio_callback
        )
        self.stream.start()
        
        # Start timer
        self.timer.start(100)  # Update every 100ms
    
    def stop_recording(self):
        if not self.recording:
            return
            
        self.recording = False
        self.status_action.setText("Processing audio...")
        self.timer.stop()
        
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
                self.tray_icon.setToolTip("⏳ Transcribing...")
                self.status_action.setText("Transcribing...")
                
                # Transcribe the audio in a separate thread
                threading.Thread(
                    target=self.transcribe_audio,
                    args=(temp_audio.name,),
                    daemon=True
                ).start()
    
    def transcribe_audio(self, audio_path):
        try:
            # Transcribe the audio
            result = self.whisper_model.transcribe(audio_path)
            self.transcribed_text = result["text"]
            
            # Signal completion
            self.signals.finished.emit(self.transcribed_text)
            
            # Clean up
            os.unlink(audio_path)
        except Exception as e:
            self.signals.status_update.emit(f"Error during transcription: {str(e)}")
            self.signals.finished.emit("")
    
    def transcription_finished(self, text):
        if text:
            # Add to history
            self.transcription_history.append((datetime.now(), text))
            self.update_history_menu()
            
            # Auto-copy if enabled
            if self.auto_copy_action.isChecked():
                pyperclip.copy(text)
                self.signals.status_update.emit("Transcription copied to clipboard!")
            
            # Show transcription window
            self.show_transcription_window(text)
        
        # Reset UI
        self.tray_icon.setToolTip("🎙️ Audio Transcriber")
        self.timer_action.setText("00:00")
        self.status_action.setText("Ready to record")
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
    
    def show_transcription_window(self, text):
        dialog = TranscriptionWindow(text)
        dialog.exec_()
    
    def quit_app(self):
        self.app.quit()
    
    def run(self):
        # Show the tray icon
        self.tray_icon.show()
        
        # Start the application
        return self.app.exec_()

if __name__ == "__main__":
    app = AudioTranscriptionApp()
    sys.exit(app.run())