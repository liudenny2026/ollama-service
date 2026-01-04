#!/usr/bin/env python3
"""
Test script for the default model (qwen3:0.6b)
"""

import requests
import json
import os
import sys
import time

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_API_BASE = f"{OLLAMA_HOST}/api"

def test_model_availability():
    """Test if the default model is available"""
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/tags")
        response.raise_for_status()
        
        models_data = response.json()
        available_models = [model.get('name') for model in models_data.get('models', [])]
        
        print(f"Available models: {available_models}")
        
        # Check for the new default model
        if "qwen3:0.6b" in available_models:
            print("✓ qwen3:0.6b model is available")
            return True
        else:
            print("✗ qwen3:0.6b model is NOT available")
            # Check for alternative qwen3 models
            qwen3_models = [model for model in available_models if "qwen3" in model]
            if qwen3_models:
                print(f"Available qwen3 models: {qwen3_models}")
            return False
    except Exception as e:
        print(f"Error checking model availability: {e}")
        return False

def test_model_generation():
    """Test the generation functionality of the model"""
    model_name = "qwen3:0.6b"
    
    # Test generation functionality
    payload = {
        "model": model_name,
        "prompt": "Hello, how are you? Please keep your response short.",
        "stream": False
    }
    
    try:
        print(f"Testing {model_name} generation functionality...")
        response = requests.post(f"{OLLAMA_API_BASE}/generate", json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get("response", "")
        
        print(f"✓ Model generated response successfully")
        print(f"Response: {response_text[:200]}...")
        
        return True
    except Exception as e:
        print(f"✗ Error testing model generation: {e}")
        return False

def test_model_chat():
    """Test the chat functionality of the model"""
    model_name = "qwen3:0.6b"
    
    # Test chat functionality
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you? Please keep your response short."
            }
        ],
        "stream": False
    }
    
    try:
        print(f"Testing {model_name} chat functionality...")
        response = requests.post(f"{OLLAMA_API_BASE}/chat", json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        assistant_response = result.get("message", {}).get("content", "")
        
        print(f"✓ Model responded successfully to chat request")
        print(f"Response: {assistant_response[:200]}...")
        
        return True
    except Exception as e:
        print(f"✗ Error testing model chat: {e}")
        return False

def main():
    print("Testing qwen3:0.6b model...")
    print("=" * 50)
    
    # Test model availability
    if not test_model_availability():
        print("Model is not available. Exiting.")
        sys.exit(1)
    
    # Test model generation
    gen_success = test_model_generation()
    
    # Test model chat
    chat_success = test_model_chat()
    
    if gen_success and chat_success:
        print("\n✓ All tests passed! The default model is working correctly.")
        return 0
    else:
        print("\n✗ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())