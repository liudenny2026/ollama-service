#!/usr/bin/env python3
"""
Streamlit-based Model Selector for Ollama
Provides a web interface for users to select and download models
"""

import streamlit as st
import subprocess
import os
import sys
import time
import json
from typing import Dict, List

# Set page config
st.set_page_config(
    page_title="Ollama Model Selector",
    page_icon="🤖",
    layout="wide"
)

# Popular models list
POPULAR_MODELS = [
    "qwen3:1.7b",
    "qwen2.5:0.5b",
    "qwen2.5:7b", 
    "qwen3:latest",
    "qwen3:0.6b",
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
        # First check if ollama command exists
        subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=10)
        # Then check if service is running
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return False

def start_ollama_service():
    """Start Ollama service in background"""
    with st.spinner("Starting Ollama service..."):
        try:
            # Check if ollama command is available
            try:
                subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=10)
            except (subprocess.SubprocessError, FileNotFoundError):
                st.error("Ollama is not installed or not in system PATH. Please install Ollama first.")
                return False
            
            # Start ollama serve in background based on OS
            import platform
            if platform.system() == "Windows":
                # On Windows, we'll start the process without redirecting output
                subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # On Unix-like systems
                os.system("ollama serve > /dev/null 2>&1 &")
            
            # Wait for service to start
            timeout = 60  # 60 seconds timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                if check_ollama_running():
                    st.success("✓ Ollama service started successfully")
                    return True
                time.sleep(5)  # Wait 5 seconds before checking again
            
            st.error("✗ Failed to start Ollama service - timed out")
            return False
        except Exception as e:
            st.error(f"✗ Error starting Ollama service: {e}")
            return False

def pull_model(model_name: str):
    """Pull model using subprocess"""
    with st.spinner(f"Downloading {model_name}..."):
        try:
            # Check if ollama command is available
            try:
                subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=10)
            except (subprocess.SubprocessError, FileNotFoundError):
                st.error("Ollama is not installed or not in system PATH. Please install Ollama first.")
                return False
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # For now, we'll just show a simple status since ollama pull doesn't provide detailed progress
            status_text.text("Starting download...")
            progress_bar.progress(10)
            
            # Command to pull model
            cmd = ["ollama", "pull", model_name]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Read output in real-time
            output_lines = []
            for line in process.stdout:
                output_lines.append(line.strip())
                status_text.text(f"Status: {line.strip()}")
                # Update progress periodically
                progress_bar.progress(min(progress_bar.progress + 10, 90))
            
            return_code = process.wait()
            
            if return_code == 0:
                progress_bar.progress(100)
                st.success(f"✓ Successfully downloaded {model_name}")
                return True
            else:
                st.error(f"✗ Failed to download {model_name}")
                st.text_area("Error details:", "\n".join(output_lines))
                return False
                
        except Exception as e:
            st.error(f"✗ Error downloading {model_name}: {e}")
            return False

def list_models():
    """List currently available models"""
    try:
        # Check if ollama command is available
        try:
            subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=10)
        except (subprocess.SubprocessError, FileNotFoundError):
            st.error("Ollama is not installed or not in system PATH. Please install Ollama first.")
            return []
        
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 1:
                        models.append(parts[0])
            return models
        else:
            return []
    except Exception as e:
        st.error(f"Error listing models: {e}")
        return []

def main():
    st.title("🤖 Ollama Model Selector")
    st.markdown("Select and download models for your Ollama service")
    
    # Check if Ollama is running
    if not check_ollama_running():
        st.warning("Ollama service is not running.")
        if st.button("Start Ollama Service"):
            start_ollama_service()
            st.rerun()
    else:
        st.success("✓ Ollama service is running")
    
    # Display currently available models
    st.subheader("📦 Currently Available Models")
    current_models = list_models()
    if current_models:
        st.write(", ".join(current_models))
    else:
        st.info("No models currently available")
    
    # Model selection
    st.subheader("🔍 Select a Model")
    
    # Create two columns for model selection
    col1, col2 = st.columns(2)
    
    with col1:
        selected_model = st.selectbox("Choose from popular models:", options=POPULAR_MODELS)
    
    with col2:
        custom_model = st.text_input("Or enter custom model name (e.g., 'llama3:8b'):")
    
    # Determine the model to use
    model_to_download = custom_model if custom_model else selected_model
    
    # Download button
    if st.button("📥 Download Selected Model", disabled=not model_to_download):
        if model_to_download:
            success = pull_model(model_to_download)
            if success:
                st.balloons()
        else:
            st.error("Please select or enter a model name")
    
    # Quick download buttons for common models
    st.subheader("⚡ Quick Download")
    cols = st.columns(3)
    quick_models = ["qwen3:1.7b", "qwen2.5:0.5b", "llama3:8b"]
    
    for i, model in enumerate(quick_models):
        with cols[i]:
            if st.button(f"Download {model}", key=f"quick_{model}"):
                success = pull_model(model)
                if success:
                    st.rerun()  # Refresh the page to update model list
    
    # Instructions
    st.subheader("ℹ️ Instructions")
    st.markdown("""
    1. Make sure Ollama service is running (click "Start Ollama Service" if needed)
    2. Select a model from the dropdown or enter a custom model name
    3. Click "Download Selected Model" to start the download
    4. Once downloaded, you can use the model with `ollama run <model_name>`
    """)

    # Available models reference
    st.subheader("📚 Available Models Reference")
    st.markdown("""
    - **Qwen3 Series**: `qwen3:latest`, `qwen3:0.6b`, `qwen3:1.7b`, `qwen3:4b`, `qwen3:14b`, `qwen3:32b`, `qwen3:235b`\n    - **Qwen2.5 Series**: `qwen2.5:0.5b`, `qwen2.5:7b`
    - **Qwen3 Series**: `qwen3:latest`, `qwen3:0.6b`, `qwen3:1.7b`, `qwen3:4b`, `qwen3:14b`, `qwen3:32b`, `qwen3:235b`
    - **Llama3 Series**: `llama3:8b`, `llama3:70b`
    - **Gemma2 Series**: `gemma2:2b`, `gemma2:9b`
    - **Other Models**: `mistral:7b`, `mixtral:8x7b`, `phi3:3.8b`, `command-r:35b`, `yi:9b`, `dbrx:132b`
    """)

if __name__ == "__main__":
    main()