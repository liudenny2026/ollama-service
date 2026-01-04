#!/usr/bin/env python3
"""
Example script to use the default qwen3:0.6b model for chat interactions
"""
import requests
import json
import os

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_API_BASE = f"{OLLAMA_HOST}/api"

class OllamaChatClient:
    def __init__(self, model_name="qwen3:0.6b"):
        self.model_name = model_name
        self.api_base = OLLAMA_API_BASE
    
    def chat(self, message, context=None):
        """Send a chat message to the model and get response"""
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "stream": False
        }
        
        if context:
            payload["context"] = context
        
        try:
            response = requests.post(f"{self.api_base}/chat", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return {
                "response": result.get("message", {}).get("content", ""),
                "context": result.get("context", []),
                "total_duration": result.get("total_duration", 0),
                "load_duration": result.get("load_duration", 0)
            }
        except Exception as e:
            print(f"Error in chat: {e}")
            return None
    
    def generate(self, prompt):
        """Generate text from a prompt using the default model"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(f"{self.api_base}/generate", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return {
                "response": result.get("response", ""),
                "total_duration": result.get("total_duration", 0),
                "load_duration": result.get("load_duration", 0)
            }
        except Exception as e:
            print(f"Error in generation: {e}")
            return None

def main():
    # Initialize the client with the default model
    client = OllamaChatClient(model_name="qwen3:0.6b")

    print("Ollama Chat Client with qwen3:0.6b (Default Model)")
    print("=" * 50)

    # Test if the default model is available
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/tags")
        response.raise_for_status()
        models_data = response.json()

        available_models = [model.get('name') for model in models_data.get('models', [])]

        if "qwen3:0.6b" in available_models:
            print("✓ qwen3:0.6b model is available")
        else:
            print("✗ qwen3:0.6b model is NOT available")
            print(f"Available models: {available_models}")
            return
    except Exception as e:
        print(f"Error checking model availability: {e}")
        return

    # Example usage
    print("\nTesting model with a simple question...")
    result = client.chat("你好，请简单介绍一下你自己。")

    if result:
        print(f"Response: {result['response'][:200]}...")
        print(f"Total duration: {result['total_duration']/1e9:.2f}s")
    else:
        print("Failed to get response from model")

    print("\nYou can now use qwen3:0.6b as the default model in your applications!")

if __name__ == "__main__":
    main()