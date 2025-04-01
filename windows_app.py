import sys
import os
import time
import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper
import pyperclip
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QLabel, QComboBox, QTextEdit, QMessageBox,
                           QSpinBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread

class AudioRecorder(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, save_dir):
        super().__init__()
        self.save_dir = save_dir
        self.sample_rate = 16000
        self.dtype = np.float32
        self.recording = False
        self.frames = []
    
    def run(self):
        try:
            # Record audio
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype=self.dtype) as stream:
                while self.recording:
                    audio_data, _ = stream.read(self.sample_rate)
                    self.frames.append(audio_data.copy())
            
            if len(self.frames) > 0:
                # Concatenate all frames
                recording = np.concatenate(self.frames, axis=0)
                
                # Generate filename with full path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.save_dir, f"recording_{timestamp}.wav")
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                
                # Save to file with explicit dtype
                sf.write(filename, recording.astype(np.float32), self.sample_rate)
                
                # Clear memory
                self.frames = []
                del recording
                
                self.finished.emit(filename)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def start_recording(self):
        self.recording = True
        self.frames = []
        self.start()
    
    def stop_recording(self):
        self.recording = False

class Transcriber(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, filename, model_name):
        super().__init__()
        self.filename = filename
        self.model_name = model_name
    
    def run(self):
        try:
            self.progress.emit("Loading model...")
            model = whisper.load_model(self.model_name)
            
            self.progress.emit("Loading audio...")
            audio_data, sample_rate = sf.read(self.filename)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            
            # Convert to float32 (what Whisper expects)
            audio_data = audio_data.astype(np.float32)
            
            self.progress.emit("Transcribing...")
            result = model.transcribe(
                audio_data,
                fp16=False,
                language='en'
            )
            
            # Clear memory
            del model
            del audio_data
            import gc
            gc.collect()
            
            self.finished.emit(result["text"])
            
        except Exception as e:
            import traceback
            self.error.emit(f"Error: {str(e)}\nTraceback: {traceback.format_exc()}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Transcriber")
        self.setGeometry(100, 100, 800, 600)
        
        # Set up recordings directory
        self.recordings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")
        os.makedirs(self.recordings_dir, exist_ok=True)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Top controls layout
        controls_layout = QHBoxLayout()
        
        # Model selection
        model_label = QLabel("Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(['tiny', 'base', 'small', 'medium'])
        self.model_combo.setCurrentText('tiny')  # Set tiny as default
        self.model_combo.currentTextChanged.connect(self.on_model_change)
        controls_layout.addWidget(model_label)
        controls_layout.addWidget(self.model_combo)
        
        # Timer display
        self.timer_label = QLabel("00:00")
        controls_layout.addWidget(self.timer_label)
        
        layout.addLayout(controls_layout)
        
        # Warning label
        warning_label = QLabel("Note: Use 'tiny' model if you experience memory issues")
        warning_label.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(warning_label)
        
        # Recording button
        self.record_button = QPushButton("Record")
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)
        
        # Status and progress
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        self.progress_label = QLabel("")
        layout.addWidget(self.progress_label)
        
        # Transcription display
        self.transcription_text = QTextEdit()
        self.transcription_text.setReadOnly(True)
        layout.addWidget(self.transcription_text)
        
        # Initialize variables
        self.last_recording = None
        self.recorder = None
        self.transcriber = None
        self.recording = False
        self.recording_start_time = None
        
        # Initialize timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
    
    def on_model_change(self, model_name):
        if model_name in ['small', 'medium']:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"Warning: {model_name} model requires significant memory")
            msg.setInformativeText("This may cause issues on systems with limited RAM.\nConsider using 'tiny' or 'base' model instead.")
            msg.setWindowTitle("Memory Usage Warning")
            msg.exec_()
    
    def update_timer(self):
        if self.recording_start_time:
            elapsed = int(time.time() - self.recording_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

    def toggle_recording(self):
        if not self.recording:
            # Start recording
            self.recording = True
            self.record_button.setText("Stop Recording")
            self.status_label.setText("Recording...")
            self.recording_start_time = time.time()
            self.timer.start(1000)  # Update timer every second
            
            # Initialize and start recorder
            self.recorder = AudioRecorder(self.recordings_dir)
            self.recorder.finished.connect(self.recording_finished)
            self.recorder.error.connect(self.handle_error)
            self.recorder.start_recording()
        else:
            # Stop recording
            self.recording = False
            self.record_button.setText("Record")
            self.status_label.setText("Processing...")
            self.timer.stop()
            self.recorder.stop_recording()
    
    def recording_finished(self, filename):
        self.last_recording = filename
        self.status_label.setText("Recording complete")
        
        # Start transcription automatically
        self.start_transcription()
    
    def start_transcription(self):
        if not self.last_recording:
            self.status_label.setText("No recording available")
            return
        
        self.transcriber = Transcriber(self.last_recording, self.model_combo.currentText())
        self.transcriber.finished.connect(self.transcription_finished)
        self.transcriber.error.connect(self.handle_error)
        self.transcriber.progress.connect(self.update_progress)
        self.transcriber.start()
    
    def transcription_finished(self, text):
        self.record_button.setEnabled(True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_text = f"[{timestamp}]\n{text}\n\n"
        self.transcription_text.append(formatted_text)
        pyperclip.copy(text)
        self.status_label.setText("Ready")
        self.progress_label.setText("")
    
    def update_progress(self, message):
        self.progress_label.setText(message)
    
    def handle_error(self, error_msg):
        self.record_button.setEnabled(True)
        QMessageBox.critical(self, "Error", error_msg)
        self.status_label.setText("Ready")
        self.progress_label.setText("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
