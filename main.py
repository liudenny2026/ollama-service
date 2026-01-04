#!/usr/bin/env python3
"""
Main entry point for Ollama Service
This script provides multiple ways to interact with the Ollama service
"""

import sys
import subprocess
import os
import argparse

def run_streamlit_app():
    """Run the Streamlit model selector app"""
    try:
        print("Starting Streamlit Model Selector...")
        print("Access the application at: http://localhost:8501")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_model_selector.py", "--server.port=8501"])
    except Exception as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)

def run_interactive_selector():
    """Run the interactive model selector"""
    try:
        print("Starting Interactive Model Selector...")
        subprocess.run([sys.executable, "model_selector.py"])
    except Exception as e:
        print(f"Error running interactive selector: {e}")
        sys.exit(1)

def run_chat_client():
    """Run the chat client with default model"""
    try:
        print("Starting Chat Client with qwen3:1.7b...")
        subprocess.run([sys.executable, "chat_with_default_model.py"])
    except Exception as e:
        print(f"Error running chat client: {e}")
        sys.exit(1)

def run_model_manager():
    """Run the model manager"""
    try:
        print("Starting Model Manager...")
        subprocess.run([sys.executable, "model_manager.py"])
    except Exception as e:
        print(f"Error running model manager: {e}")
        sys.exit(1)

def run_test():
    """Run the default model test"""
    try:
        print("Running Default Model Test...")
        subprocess.run([sys.executable, "test_default_model.py"])
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Ollama Service Manager')
    parser.add_argument('command', nargs='?', default='streamlit',
                        choices=['streamlit', 'interactive', 'chat', 'manager', 'test', 'help'],
                        help='Command to run (default: streamlit)')
    
    args = parser.parse_args()
    
    print("Ollama Service Manager")
    print("=" * 50)
    print("Available commands:")
    print("  streamlit  - Run Streamlit model selector (default)")
    print("  interactive - Run interactive model selector")
    print("  chat      - Run chat client with default model")
    print("  manager   - Run model manager")
    print("  test      - Run default model test")
    print("  help      - Show this help message")
    print("=" * 50)
    
    if args.command == 'streamlit':
        run_streamlit_app()
    elif args.command == 'interactive':
        run_interactive_selector()
    elif args.command == 'chat':
        run_chat_client()
    elif args.command == 'manager':
        run_model_manager()
    elif args.command == 'test':
        run_test()
    elif args.command == 'help':
        parser.print_help()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()