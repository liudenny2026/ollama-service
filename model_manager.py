#!/usr/bin/env python3
"""
Ollama Model Manager
This script provides functionality to manage Ollama models including downloading, listing, and checking model status.
"""

import os
import sys
import time
import requests
import json
from typing import List, Dict, Optional

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_API_BASE = f"{OLLAMA_HOST}/api"

class OllamaModelManager:
    def __init__(self, host: str = None):
        self.host = host or OLLAMA_HOST
        self.api_base = f"{self.host}/api"
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make a request to the Ollama API"""
        url = f"{self.api_base}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None
    
    def list_models(self) -> List[Dict]:
        """List all available models"""
        result = self._make_request('GET', '/tags')
        if result and 'models' in result:
            return result['models']
        elif result and isinstance(result, list):
            return result
        return []
    
    def show_model_info(self, model_name: str) -> Dict:
        """Show detailed information about a specific model"""
        data = {"name": model_name}
        return self._make_request('POST', '/show', data)
    
    def pull_model(self, model_name: str, stream: bool = True) -> bool:
        """Download/pull a model from Ollama registry"""
        print(f"Pulling model: {model_name}")
        
        data = {
            "name": model_name,
            "stream": stream
        }
        
        try:
            response = requests.post(f"{self.api_base}/pull", json=data, stream=True)
            response.raise_for_status()
            
            # Process the streaming response
            for line in response.iter_lines():
                if line:
                    try:
                        progress = json.loads(line.decode('utf-8'))
                        if 'status' in progress:
                            print(f"Status: {progress['status']}")
                        if 'completed' in progress and 'total' in progress:
                            percent = (progress['completed'] / progress['total']) * 100 if progress['total'] > 0 else 0
                            print(f"Progress: {percent:.1f}%")
                    except json.JSONDecodeError:
                        continue
            
            print(f"Successfully pulled model: {model_name}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to pull model {model_name}: {e}")
            return False
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a model from local storage"""
        data = {"name": model_name}
        result = self._make_request('DELETE', '/delete', data)
        return result is not None
    
    def check_connection(self) -> bool:
        """Check if the Ollama service is accessible"""
        try:
            response = requests.get(f"{self.api_base}/tags", timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

def main():
    """Main function to demonstrate the model manager"""
    manager = OllamaModelManager()
    
    if not manager.check_connection():
        print("Error: Cannot connect to Ollama service")
        sys.exit(1)
    
    print("Ollama Model Manager")
    print("=" * 30)
    
    if len(sys.argv) < 2:
        print("Usage: python model_manager.py [list|pull|delete] [model_name]")
        print("  list   - List all available models")
        print("  pull   - Download a model (e.g., 'pull qwen3:1.7b')")
        print("  delete - Delete a model (e.g., 'delete qwen3:1.7b')")
        print("")
        
        # List current models
        print("Current models:")
        models = manager.list_models()
        if models:
            for model in models:
                print(f"  - {model.get('name', 'Unknown')}")
        else:
            print("  No models currently available")
        
        print("")
        
        # Default: pull qwen3:1.7b if not already present
        model_name = "qwen3:1.7b"
        model_exists = any(model.get('name') == model_name for model in models)
        
        if not model_exists:
            print(f"Default model {model_name} not found. Pulling now...")
            success = manager.pull_model(model_name)
            if success:
                print(f"Successfully downloaded {model_name}")
            else:
                print(f"Failed to download {model_name}")
        else:
            print(f"Default model {model_name} already exists")
        
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        print("Available models:")
        models = manager.list_models()
        if models:
            for model in models:
                print(f"  - {model.get('name', 'Unknown')}")
        else:
            print("  No models available")
    
    elif command == 'pull' and len(sys.argv) > 2:
        model_name = sys.argv[2]
        success = manager.pull_model(model_name)
        if success:
            print(f"Successfully pulled model: {model_name}")
        else:
            print(f"Failed to pull model: {model_name}")
    
    elif command == 'delete' and len(sys.argv) > 2:
        model_name = sys.argv[2]
        success = manager.delete_model(model_name)
        if success:
            print(f"Successfully deleted model: {model_name}")
        else:
            print(f"Failed to delete model: {model_name}")
    
    else:
        print("Invalid command. Use 'list', 'pull', or 'delete' with appropriate arguments.")

if __name__ == "__main__":
    main()