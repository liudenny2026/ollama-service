#!/usr/bin/env python3
"""
Interactive Model Selector for Ollama
Allows users to select from popular models or enter custom model names
Downloads models using domestic mirror for faster speed
"""

import os
import subprocess
import sys
import time
from typing import List, Optional

# Popular models list
POPULAR_MODELS = [
    "qwen3:0.6b",
    "qwen2.5:0.5b",
    "qwen2.5:7b",
    "qwen3:latest",
    "qwen3:1.7b",
    "qwen3:4b",
    "qwen3:14b",
    "qwen3:32b",
    "qwen3:235b",
    "llama3:8b",
    "llama3:70b",
    "gemma2:2b",
    "gemma2:9b",
    "mistral:7b",
    "mixtral:8x7b",
    "phi3:3.8b",
    "command-r:35b",
    "yi:9b",
    "dbrx:132b"
]

def check_ollama_running() -> bool:
    """Check if Ollama service is running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False

def start_ollama_service():
    """Start Ollama service in background"""
    print("Starting Ollama service...")
    try:
        # Start ollama serve in background
        os.system("ollama serve > /dev/null 2>&1 &")
        time.sleep(10)  # Wait for service to start
        
        if check_ollama_running():
            print("✓ Ollama service started successfully")
        else:
            print("✗ Failed to start Ollama service")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error starting Ollama service: {e}")
        sys.exit(1)

def display_model_menu():
    """Display available models for selection"""
    print("\nAvailable models:")
    print("=" * 50)
    for i, model in enumerate(POPULAR_MODELS, 1):
        print(f"{i:2d}. {model}")
    print(f"{'0':>2s}. Enter custom model name")
    print("=" * 50)

def get_user_selection() -> str:
    """Get model selection from user"""
    while True:
        try:
            choice = input(f"\nSelect a model (1-{len(POPULAR_MODELS)}) or 0 for custom: ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                custom_model = input("Enter custom model name (e.g., 'llama3:8b'): ").strip()
                if custom_model:
                    return custom_model
                else:
                    print("Invalid input. Please enter a model name.")
                    continue
            elif 1 <= choice_num <= len(POPULAR_MODELS):
                return POPULAR_MODELS[choice_num - 1]
            else:
                print(f"Please enter a number between 0 and {len(POPULAR_MODELS)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)

def pull_model_with_mirror(model_name: str):
    """Pull model using domestic mirror for faster download"""
    print(f"\nDownloading model: {model_name}")
    print("Using domestic mirror for faster download...")
    
    # Set Ollama mirror environment variables for faster download in China
    env = os.environ.copy()
    env["OLLAMA_HOST"] = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
    
    # Use subprocess to pull the model with timeout
    try:
        # Command to pull model
        cmd = ["ollama", "pull", model_name]
        
        print(f"Executing: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=env
        )
        
        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        return_code = process.poll()
        
        if return_code == 0:
            print(f"\n✓ Successfully downloaded {model_name}")
            return True
        else:
            print(f"\n✗ Failed to download {model_name}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n✗ Download timed out for {model_name}")
        return False
    except Exception as e:
        print(f"\n✗ Error downloading {model_name}: {e}")
        return False

def main():
    print("Ollama Model Selector")
    print("=====================")
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("Ollama service is not running.")
        start_service = input("Start Ollama service? (y/n): ").strip().lower()
        if start_service in ['y', 'yes', '']:
            start_ollama_service()
        else:
            print("Ollama service is required to download models.")
            sys.exit(1)
    else:
        print("✓ Ollama service is running")
    
    # Display model menu and get user selection
    display_model_menu()
    selected_model = get_user_selection()
    
    print(f"\nSelected model: {selected_model}")
    
    # Confirm download
    confirm = input(f"Download {selected_model}? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', '']:
        print("Download cancelled")
        return
    
    # Pull the selected model
    success = pull_model_with_mirror(selected_model)
    
    if success:
        print(f"\n✓ Model {selected_model} is ready to use!")
        print("You can now run the model using: ollama run", selected_model)
    else:
        print(f"\n✗ Failed to download {selected_model}")
        sys.exit(1)

if __name__ == "__main__":
    main()