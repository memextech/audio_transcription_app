import rumps
import sounddevice as sd
import numpy as np
import wavio
import tempfile
import os
import time
import mlx_whisper
import threading
import queue
import pyperclip
from datetime import datetime

class TranscriptionWindow(rumps.Window):
    def __init__(self, title, message, dimensions=(500, 300)):
        # Create a window with a text field instead of just a message
        super(TranscriptionWindow, self).__init__(
            title=title,
            message="",  # Empty message as we'll use a text field
            dimensions=dimensions,
            ok="Copy & Close",
            cancel=None  # Remove the second button to simplify
        )
        # Set the default text in the main text field
        self.default_text = message
        
    def run(self):
        # Override run to set the text field content
        self._textfield.setStringValue_(self.default_text)
        self._textfield.setEditable_(True)  # Make the text editable
        self._textfield.setSelectable_(True)  # Make the text selectable
        return super(TranscriptionWindow, self).run()

class AudioTranscriptionApp(rumps.App):
    def __init__(self):
        super(AudioTranscriptionApp, self).__init__(
            name="Audio Transcriber",
            title="🎙️",
            quit_button=None  # Custom quit button
        )
        
        # Initialize Whisper model
        # Using a valid model from Hugging Face
        self.model_path = "mlx-community/whisper-medium-mlx"  # Hugging Face medium model
        
        # Recording state
        self.recording = False
        self.audio_data = []
        self.audio_queue = queue.Queue()
        self.sample_rate = 44100
        self.start_time = None
        self.transcription_history = []
        
        # Menu items
        self.start_button = rumps.MenuItem(
            title="Start Recording",
            callback=self.start_recording
        )
        self.stop_button = rumps.MenuItem(
            title="Stop Recording",
            callback=self.stop_recording
        )
        self.stop_button.set_callback(None)  # Disable initially
        
        self.timer_item = rumps.MenuItem(title="00:00")
        self.timer_item.set_callback(None)  # Make it non-clickable
        
        self.status_item = rumps.MenuItem(title="Ready to record")
        self.status_item.set_callback(None)
        
        # History submenu
        self.history_menu = rumps.MenuItem("Recent Transcriptions")
        no_history = rumps.MenuItem("No recent transcriptions")
        no_history.set_callback(None)
        self.history_menu.add(no_history)
        
        # Settings submenu
        self.settings_menu = rumps.MenuItem("Settings")
        self.auto_copy = rumps.MenuItem("Auto-copy to clipboard", 
                                      callback=self.toggle_auto_copy)
        self.auto_copy.state = True  # Enable by default
        self.settings_menu.add(self.auto_copy)
        
        # Add menu items
        self.menu = [
            self.start_button,
            self.stop_button,
            None,  # Separator
            self.status_item,
            self.timer_item,
            None,  # Separator
            self.history_menu,
            None,  # Separator
            self.settings_menu,
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]
        
        self.transcribed_text = None
    
    def update_history_menu(self):
        # Remove all existing items
        if len(self.history_menu._menu.itemArray()):
            for _ in range(len(self.history_menu._menu.itemArray())):
                self.history_menu._menu.removeItemAtIndex_(0)
        
        if not self.transcription_history:
            no_history = rumps.MenuItem("No recent transcriptions")
            no_history.set_callback(None)
            self.history_menu.add(no_history)
        else:
            # Add recent transcriptions (last 5)
            for timestamp, text in self.transcription_history[-5:]:
                # Create a preview (first 30 chars)
                preview = text[:30] + "..." if len(text) > 30 else text
                menu_item = rumps.MenuItem(
                    f"{timestamp.strftime('%H:%M:%S')}: {preview}",
                    callback=lambda x, t=text: self.show_transcription_from_history(t)
                )
                self.history_menu.add(menu_item)
            
            # Add clear history option
            self.history_menu.add(None)  # Separator
            self.history_menu.add(
                rumps.MenuItem("Clear History", callback=self.clear_history)
            )
    
    def clear_history(self, _):
        self.transcription_history = []
        self.update_history_menu()
    
    def show_transcription_from_history(self, text):
        self.show_transcription_window(text)
    
    def toggle_auto_copy(self, sender):
        sender.state = not sender.state
    
    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(status)
        self.audio_queue.put(indata.copy())
    
    def update_timer(self):
        while self.recording:
            elapsed = time.time() - self.start_time
            mins, secs = divmod(int(elapsed), 60)
            self.timer_item.title = f"⏱️ {mins:02d}:{secs:02d}"
            time.sleep(0.1)
    
    def start_recording(self, _):
        self.recording = True
        self.audio_data = []
        self.start_time = time.time()
        
        # Update UI
        self.start_button.set_callback(None)  # Disable start button
        self.stop_button.set_callback(self.stop_recording)  # Enable stop button
        self.title = "⏹️"  # Change menu bar icon to stop icon
        self.status_item.title = "Recording in progress..."
        self.start_button.title = "Recording..."
        
        # Start audio stream
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            callback=self.audio_callback
        )
        self.stream.start()
        
        # Start timer update thread
        threading.Thread(target=self.update_timer, daemon=True).start()
    
    def stop_recording(self, _):
        if not self.recording:
            return
            
        self.recording = False
        self.status_item.title = "Processing audio..."
        
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
                self.title = "⏳"
                self.status_item.title = "Transcribing..."
                
                # Transcribe the audio
                result = mlx_whisper.transcribe(temp_audio.name, path_or_hf_repo=self.model_path)
                self.transcribed_text = result['text']
                
                # Add to history
                self.transcription_history.append((datetime.now(), self.transcribed_text))
                self.update_history_menu()
                
                # Auto-copy if enabled
                if self.auto_copy.state:
                    pyperclip.copy(self.transcribed_text)
                    self.status_item.title = "Transcription copied to clipboard!"
                
                # Show transcription window
                self.show_transcription_window(self.transcribed_text)
                
                # Clean up
                os.unlink(temp_audio.name)
        
        # Reset UI
        self.title = "🎙️"
        self.timer_item.title = "00:00"
        self.status_item.title = "Ready to record"
        self.start_button.title = "Start Recording"
        self.start_button.set_callback(self.start_recording)  # Enable start button
        self.stop_button.set_callback(None)  # Disable stop button
    
    def show_transcription_window(self, text):
        window = TranscriptionWindow(
            title="✨ Transcription",
            message=text
        )
        response = window.run()
        
        # Copy to clipboard when user clicks "Copy & Close"
        if response.clicked:
            pyperclip.copy(text)
            self.status_item.title = "Transcription copied to clipboard!"
    
    def quit_app(self, _):
        rumps.quit_application()

if __name__ == "__main__":
    AudioTranscriptionApp().run()
