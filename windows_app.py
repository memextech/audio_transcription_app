import sys
import os
import time
import tempfile
import threading
import queue
import logging
from datetime import datetime
import numpy as np
import sounddevice as sd
import wavio
import pyperclip
import whisper
import soundfile as sf
from scipy import signal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction, 
                            QDialog, QVBoxLayout, QTextEdit, QPushButton,
                            QHBoxLayout, QLabel, QComboBox, QWidget)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("whisper_app_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WhisperApp")

class TranscriptionSignals(QObject):
    """Signal class for thread communication"""
    finished = pyqtSignal(str)
    status_update = pyqtSignal(str)

class TranscriptionWindow(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transcription Results")
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Transcriber")
        self.setMinimumSize(600, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Status label
        self.status_label = QLabel("Ready to record")
        font = QFont()
        font.setPointSize(12)
        self.status_label.setFont(font)
        layout.addWidget(self.status_label)
        
        # Timer label
        self.timer_label = QLabel("00:00")
        self.timer_label.setFont(font)
        layout.addWidget(self.timer_label)
        
        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium"])
        self.model_combo.setCurrentText("base")
        self.model_combo.currentTextChanged.connect(self.change_model)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # Auto-copy checkbox
        self.auto_copy_checkbox = QPushButton("Auto-copy to clipboard")
        self.auto_copy_checkbox.setCheckable(True)
        self.auto_copy_checkbox.setChecked(True)
        layout.addWidget(self.auto_copy_checkbox)
        
        # Add a note about model selection
        model_note = QLabel("Note: Larger models provide better accuracy but use more memory and take longer to process.")
        model_note.setWordWrap(True)
        layout.addWidget(model_note)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Start recording button
        self.start_button = QPushButton("Start Recording")
        self.start_button.clicked.connect(self.start_recording)
        button_layout.addWidget(self.start_button)
        
        # Stop recording button
        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Transcription history
        layout.addWidget(QLabel("Recent Transcriptions:"))
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)
        
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
        
        # Timer for updating recording time
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # Initialize the model
        self.load_model()
    
    def load_model(self):
        try:
            logger.info(f"Loading Whisper model: {self.current_model}")
            self.status_label.setText(f"Loading {self.current_model} model...")
            self.whisper_model = whisper.load_model(self.current_model)
            logger.info("Model loaded successfully")
            self.status_label.setText("Ready to record")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}", exc_info=True)
            self.status_label.setText(f"Error loading model: {str(e)}")
    
    def change_model(self, model_name):
        logger.info(f"Changing model to: {model_name}")
        self.current_model = model_name
        self.load_model()
    
    def update_timer(self):
        if self.recording and self.start_time:
            elapsed = time.time() - self.start_time
            mins, secs = divmod(int(elapsed), 60)
            self.timer_label.setText(f"Recording: {mins:02d}:{secs:02d}")
    
    def update_status(self, message):
        self.status_label.setText(message)
    
    def audio_callback(self, indata, frames, time_info, status):
        if status:
            logger.warning(f"Audio callback status: {status}")
        self.audio_queue.put(indata.copy())
    
    def start_recording(self):
        logger.info("Starting recording")
        self.recording = True
        self.audio_data = []
        self.start_time = time.time()
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Recording in progress...")
        
        # Start audio stream
        try:
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=self.audio_callback
            )
            self.stream.start()
            logger.info("Audio stream started")
        except Exception as e:
            logger.error(f"Error starting audio stream: {str(e)}", exc_info=True)
            self.status_label.setText(f"Error: {str(e)}")
            self.recording = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            return
        
        # Start timer
        self.timer.start(100)  # Update every 100ms
    
    def stop_recording(self):
        if not self.recording:
            return
            
        logger.info("Stopping recording")
        self.recording = False
        self.status_label.setText("Processing audio...")
        self.timer.stop()
        
        # Stop the stream
        try:
            self.stream.stop()
            self.stream.close()
            logger.info("Audio stream stopped")
        except Exception as e:
            logger.error(f"Error stopping audio stream: {str(e)}", exc_info=True)
        
        # Process all remaining audio in queue
        while not self.audio_queue.empty():
            self.audio_data.extend(self.audio_queue.get()[:, 0])
        
        # Convert to numpy array
        recording = np.array(self.audio_data)
        
        if len(recording) > 0:
            logger.info(f"Recording captured: {len(recording)} samples")
            
            # Update UI to show transcribing status
            self.status_label.setText("Transcribing...")
            
            # Transcribe the audio directly
            threading.Thread(
                target=self.transcribe_audio,
                args=(recording,),
                daemon=True
            ).start()
        else:
            logger.warning("No audio data captured")
            self.status_label.setText("No audio data captured")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
    
    def transcribe_audio(self, audio_data):
        try:
            logger.info(f"Transcribing audio, {len(audio_data)} samples")
            
            # Ensure audio data is float32
            if audio_data.dtype != np.float32:
                logger.info(f"Converting audio from {audio_data.dtype} to float32")
                audio_data = audio_data.astype(np.float32)
            
            # Normalize audio data to be between -1 and 1
            max_abs = np.max(np.abs(audio_data))
            if max_abs > 1.0:
                logger.info(f"Normalizing audio data (max amplitude: {max_abs})")
                audio_data = audio_data / max_abs
            elif max_abs < 0.1:
                logger.warning(f"Audio signal may be too quiet (max amplitude: {max_abs})")
            
            # Transcribe the audio using the loaded data
            logger.info("Starting transcription with Whisper model")
            result = self.whisper_model.transcribe(audio_data)
            self.transcribed_text = result["text"]
            logger.info(f"Transcription result: {self.transcribed_text}")
            
            # Signal completion
            self.signals.finished.emit(self.transcribed_text)
            
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}", exc_info=True)
            self.signals.status_update.emit(f"Error during transcription: {str(e)}")
            self.signals.finished.emit("")
    
    def transcription_finished(self, text):
        if text:
            logger.info("Transcription finished successfully")
            # Add to history
            self.transcription_history.append((datetime.now(), text))
            
            # Update history display
            self.update_history_display()
            
            # Auto-copy if enabled
            if self.auto_copy_checkbox.isChecked():
                pyperclip.copy(text)
                self.signals.status_update.emit("Transcription copied to clipboard!")
                logger.info("Transcription copied to clipboard")
            
            # Show transcription window
            self.show_transcription_window(text)
        else:
            logger.warning("Transcription finished with empty result")
        
        # Reset UI
        self.timer_label.setText("00:00")
        self.status_label.setText("Ready to record")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
    def update_history_display(self):
        self.history_text.clear()
        for timestamp, text in self.transcription_history:
            self.history_text.append(f"<b>{timestamp.strftime('%H:%M:%S')}</b>: {text}")
            self.history_text.append("<hr>")
    
    def show_transcription_window(self, text):
        dialog = TranscriptionWindow(text, self)
        dialog.exec_()

def main():
    try:
        logger.info("Starting Audio Transcription App")
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle("Fusion")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        logger.info("Main window displayed")
        
        # Run application
        exit_code = app.exec_()
        logger.info(f"Application exited with code: {exit_code}")
        return exit_code
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
