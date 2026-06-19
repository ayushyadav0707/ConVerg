import subprocess
import os
import sys
import time

def main():
    print("=== Starting House Price Predictor Full-Stack App ===")
    
    # 1. Start the Flask Backend
    print("[1/2] Starting Python Flask Backend...")
    backend_dir = os.path.join(os.getcwd(), "backend")
    # We use sys.executable to ensure the same Python environment is used
    backend_process = subprocess.Popen([sys.executable, "app.py"], cwd=backend_dir)
    
    # Give the backend a second to initialize
    time.sleep(2)
    
    # 2. Start the React Frontend
    print("[2/2] Starting React Vite Frontend...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    # shell=True is required on Windows for npm
    frontend_process = subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir, shell=True)
    
    print("\n" + "="*60)
    print("🚀 APPLICATION IS RUNNING!")
    print("Backend API is running on: http://127.0.0.1:5000")
    print("Frontend UI is running on: http://localhost:5173")
    print("Open your browser and click the localhost link above!")
    print("Press Ctrl+C here in the terminal to stop both servers.")
    print("="*60 + "\n")
    
    try:
        # Keep the main script alive while servers are running
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down both servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Successfully closed.")

if __name__ == "__main__":
    main()
