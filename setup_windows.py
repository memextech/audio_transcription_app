import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")

def install_uv():
    """Install uv package manager if not already installed"""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("uv package manager is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing uv package manager...")
        try:
            subprocess.run(
                ["pip", "install", "uv"],
                check=True
            )
            print("uv package manager installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing uv: {e}")
            sys.exit(1)

def setup_virtual_environment():
    """Create and activate a virtual environment"""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("Virtual environment already exists")
    else:
        print("Creating virtual environment...")
        try:
            subprocess.run(
                ["uv", "venv"],
                check=True
            )
            print("Virtual environment created successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
    
    return venv_path

def install_dependencies(venv_path):
    """Install required dependencies"""
    print("Installing dependencies...")
    
    # Create requirements_windows.txt with PyQt5 instead of rumps
    with open("requirements_windows.txt", "w") as f:
        f.write("""lightning-whisper-mlx
PyQt5
sounddevice
wavio
pillow
pyperclip
tqdm
""")
    
    try:
        # Use uv to install dependencies
        subprocess.run(
            ["uv", "pip", "install", "-r", "requirements_windows.txt"],
            check=True
        )
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def download_model():
    """Download the Whisper model"""
    print("Downloading Whisper model...")
    try:
        # Run the download_model.py script
        subprocess.run(
            [sys.executable, "download_model.py"],
            check=True
        )
        print("Model downloaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading model: {e}")
        sys.exit(1)

def create_shortcut():
    """Create a shortcut to launch the application"""
    print("Creating application shortcut...")
    
    # Create a batch file to launch the application
    with open("launch_audio_transcriber.bat", "w") as f:
        f.write(f"""@echo off
cd /d "%~dp0"
call .venv\\Scripts\\activate.bat
python windows_app.py
""")
    
    print("Shortcut created: launch_audio_transcriber.bat")
    
    # Try to create a Windows shortcut (.lnk) file
    try:
        import win32com.client
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut("Audio Transcriber.lnk")
        shortcut.Targetpath = os.path.abspath("launch_audio_transcriber.bat")
        shortcut.WorkingDirectory = os.path.abspath(".")
        shortcut.IconLocation = os.path.abspath(os.path.join("assets", "audio_transcriber_icon.png"))
        shortcut.save()
        
        print("Windows shortcut created: Audio Transcriber.lnk")
    except:
        print("Could not create Windows shortcut. You can use the batch file instead.")

def main():
    """Main setup function"""
    print("=== Audio Transcriber Windows Setup ===")
    
    # Check Python version
    check_python_version()
    
    # Install uv package manager
    install_uv()
    
    # Setup virtual environment
    venv_path = setup_virtual_environment()
    
    # Install dependencies
    install_dependencies(venv_path)
    
    # Download model
    download_model()
    
    # Create shortcut
    create_shortcut()
    
    print("\n=== Setup Complete ===")
    print("To start the application, double-click 'launch_audio_transcriber.bat' or 'Audio Transcriber.lnk'")

if __name__ == "__main__":
    main()