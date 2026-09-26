"""
Secure frontend launcher for Healthcare Planning Assistant
"""

import subprocess
import sys
import os

def get_python_executable():
    """Get the virtual environment Python if available, else sys.executable"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_root, "venv", "bin", "python")
    if os.path.exists(venv_python):
        return venv_python
    return sys.executable

def main():
    """Launch the secure Streamlit frontend with authentication"""
    print("🔐 Starting Secure Healthcare Planning Assistant Frontend...")
    print("🌐 Frontend will be available at: http://localhost:8503")
    print("🔒 This version includes user authentication")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        secure_script = os.path.join(project_dir, "frontend", "secure_app.py")
        if not os.path.exists(secure_script):
            print("❌ Error: frontend/secure_app.py not found. Please run from the project directory.")
            return
        
        py_exe = get_python_executable()
        os.chdir(os.path.join(project_dir, "frontend"))
        subprocess.run([py_exe, "-m", "streamlit", "run", "secure_app.py", "--server.port", "8503"])
        
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

if __name__ == "__main__":
    main()
