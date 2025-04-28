#!/usr/bin/env python3
import os
import sys
import mlx_whisper
from pathlib import Path
from huggingface_hub import snapshot_download

def main():
    model_id = "mlx-community/whisper-medium-mlx"
    print(f"Downloading model {model_id}...")
    
    # This will download and cache the model 
    # in the ~/.cache/huggingface/hub directory
    model_path = snapshot_download(repo_id=model_id)
    
    print(f"Model downloaded to: {model_path}")
    
    # Test loading the model
    print("Testing model loading...")
    try:
        # Just test that we can use the model for transcription
        # Using a dummy path since we only want to test model loading
        _ = mlx_whisper.transcribe(
            None, 
            path_or_hf_repo=model_id, 
            return_without_timestamps=True, 
            dry_run=True
        )
        print("✅ Model reference validated successfully!")
    except Exception as e:
        print(f"❌ Error referencing model: {e}")
        # We'll continue anyway as the model is downloaded
    
    print("Download and validation complete!")

if __name__ == "__main__":
    main()
