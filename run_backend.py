"""
Backend launcher for Healthcare Planning Assistant API
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
    """Launch the FastAPI backend server"""
    print("🚀 Starting Healthcare Planning Assistant Backend...")
    print("📍 API will be available at: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        api_script = os.path.join(project_dir, "api", "main.py")
        if not os.path.exists(api_script):
            print("❌ Error: api/main.py not found. Please run from the project directory.")
            return
        
        py_exe = get_python_executable()
        os.chdir(os.path.join(project_dir, "api"))
        subprocess.run([py_exe, "main.py"])
        
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped by user")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

if __name__ == "__main__":
    main()
