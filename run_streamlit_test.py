#!/usr/bin/env python3
"""
Test script for Streamlit Model Selector
"""

import subprocess
import sys
import time
import requests
import threading
import os

def check_streamlit_running(port=8501):
    """Check if Streamlit is running on the specified port"""
    try:
        response = requests.get(f"http://localhost:{port}")
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def run_streamlit_app():
    """Run the Streamlit application in a subprocess"""
    try:
        # Start Streamlit app
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_model_selector.py", 
            f"--server.port=8501",
            "--server.headless=true"  # Run in headless mode for testing
        ])
        
        print("Streamlit app started. PID:", process.pid)
        return process
    except Exception as e:
        print(f"Error starting Streamlit app: {e}")
        return None

def test_streamlit_interface():
    """Test the Streamlit interface"""
    print("Testing Streamlit Model Selector...")
    
    # Start the Streamlit app in a separate thread
    print("Starting Streamlit application...")
    process = run_streamlit_app()
    
    if not process:
        print("Failed to start Streamlit application")
        return False
    
    # Wait a bit for the app to start
    time.sleep(5)
    
    # Check if the app is accessible
    if check_streamlit_running():
        print("✓ Streamlit application is running and accessible")
        
        # Test getting the page
        try:
            response = requests.get("http://localhost:8501")
            if response.status_code == 200:
                print("✓ Successfully accessed Streamlit interface")
                
                # Check if key elements are present in the page
                content = response.text
                if "Ollama Model Selector" in content:
                    print("✓ Found expected content in the page")
                else:
                    print("⚠ Content check failed - page loaded but content may be different than expected")
                    
                return True
            else:
                print(f"✗ Failed to access Streamlit interface. Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error accessing Streamlit interface: {e}")
            return False
    else:
        print("✗ Streamlit application is not accessible")
        return False
    finally:
        # Clean up - terminate the process
        if process:
            print("Stopping Streamlit application...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

def test_model_functions():
    """Test model-related functions"""
    print("\nTesting model-related functions...")
    
    # Test if ollama command is available
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Ollama is installed and accessible")
        else:
            print("✗ Ollama is not accessible")
            return False
    except FileNotFoundError:
        print("✗ Ollama is not installed")
        return False
    
    # Test if we can list models
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Can list models with Ollama")
        else:
            print("✗ Cannot list models with Ollama")
            return False
    except Exception as e:
        print(f"✗ Error listing models: {e}")
        return False
    
    return True

def main():
    print("Streamlit Model Selector Test")
    print("=" * 50)
    
    # Test model functions first
    model_test_result = test_model_functions()
    
    if not model_test_result:
        print("\nModel functions test failed. Cannot proceed with Streamlit test.")
        return 1
    
    # Test Streamlit interface
    streamlit_test_result = test_streamlit_interface()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Model Functions: {'✓ PASSED' if model_test_result else '✗ FAILED'}")
    print(f"Streamlit Interface: {'✓ PASSED' if streamlit_test_result else '✗ FAILED'}")
    
    if model_test_result and streamlit_test_result:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())