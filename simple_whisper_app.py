import sys  
import os  
import time  
import threading  
import queue  
import numpy as np  
import sounddevice as sd  
import whisper  
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QTextEdit  
from PyQt5.QtCore import Qt, QTimer  
class MainWindow(QMainWindow):  
    def __init__(self):  
        super().__init__()  
        self.setWindowTitle("Simple Audio Transcriber")  
        self.setMinimumSize(500, 400)  
        central_widget = QWidget()  
        self.setCentralWidget(central_widget)  
        layout = QVBoxLayout(central_widget)  
        self.status_label = QLabel("Ready to record")  
        layout.addWidget(self.status_label)  
        self.start_button = QPushButton("Start Recording")  
        self.start_button.clicked.connect(self.start_recording)  
        layout.addWidget(self.start_button)  
        self.stop_button = QPushButton("Stop Recording")  
        self.stop_button.clicked.connect(self.stop_recording)  
        self.stop_button.setEnabled(False)  
        layout.addWidget(self.stop_button)  
        self.result_text = QTextEdit()  
        self.result_text.setReadOnly(True)  
        layout.addWidget(self.result_text)  
        # Recording state  
        self.recording = False  
        self.audio_data = []  
        self.audio_queue = queue.Queue()  
        self.sample_rate = 16000  
        # Load model  
        self.status_label.setText("Loading model...")  
        self.whisper_model = whisper.load_model("tiny")  
        self.status_label.setText("Ready to record")  
    def audio_callback(self, indata, frames, time_info, status):  
        self.audio_queue.put(indata.copy())  
    def start_recording(self):  
        self.recording = True  
        self.audio_data = []  
        self.start_button.setEnabled(False)  
        self.stop_button.setEnabled(True)  
        self.status_label.setText("Recording...")  
        self.stream = sd.InputStream(channels=1, samplerate=self.sample_rate, callback=self.audio_callback)  
        self.stream.start()  
    def stop_recording(self):  
        if not self.recording:  
            return  
        self.recording = False  
        self.status_label.setText("Processing audio...")  
        self.stream.stop()  
        self.stream.close()  
        while not self.audio_queue.empty():  
            self.audio_data.extend(self.audio_queue.get()[:, 0])  
        recording = np.array(self.audio_data)  
        if len(recording)  
            self.status_label.setText("Transcribing...")  
            threading.Thread(target=self.transcribe_audio, args=(recording,), daemon=True).start()  
        else:  
            self.status_label.setText("No audio captured")  
            self.start_button.setEnabled(True)  
            self.stop_button.setEnabled(False)  
    def transcribe_audio(self, audio_data):  
        try:  
            result = self.whisper_model.transcribe(audio_data)  
            text = result["text"]  
            # Update UI in the main thread  
            QApplication.instance().postEvent(self, TranscriptionEvent(text))  
        except Exception as e:  
            QApplication.instance().postEvent(self, TranscriptionEvent(f"Error: {str(e)}"))  
class TranscriptionEvent(QEvent):  
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())  
    def __init__(self, text):  
        super().__init__(TranscriptionEvent.EVENT_TYPE)  
        self.text = text  
class MainWindow(MainWindow):  
    def event(self, event):  
        if event.type() == TranscriptionEvent.EVENT_TYPE:  
            self.result_text.setText(event.text)  
