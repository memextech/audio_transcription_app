#!/usr/bin/env python3
import os
import sys
import requests
from pathlib import Path
from tqdm import tqdm

MODEL_URL = "https://huggingface.co/mlx-community/whisper-distil-medium.en-mlx/resolve/main/weights.npz"
MODEL_DIR = Path(__file__).parent / "mlx_models" / "distil-medium.en"

def download_file(url: str, filepath: Path, chunk_size: int = 8192):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    progress_bar = tqdm(
        total=total_size,
        unit='iB',
        unit_scale=True,
        desc=f"Downloading model"
    )
    
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            progress_bar.update(len(chunk))
            f.write(chunk)
    
    progress_bar.close()

def main():
    model_path = MODEL_DIR / "weights.npz"
    
    if model_path.exists():
        print(f"Model already exists at {model_path}")
        return
    
    print(f"Downloading model to {model_path}")
    download_file(MODEL_URL, model_path)
    print("Download complete!")

if __name__ == "__main__":
    main()
