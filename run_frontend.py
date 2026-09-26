"""
Frontend launcher for Healthcare Planning Assistant
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
    """Launch the Streamlit frontend"""
    print("🖥️  Starting Healthcare Planning Assistant Frontend...")
    print("🌐 Frontend will be available at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_script = os.path.join(project_dir, "frontend", "streamlit_app.py")
        if not os.path.exists(frontend_script):
            print("❌ Error: frontend/streamlit_app.py not found. Please run from the project directory.")
            return
        
        py_exe = get_python_executable()
        os.chdir(os.path.join(project_dir, "frontend"))
        subprocess.run([py_exe, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"])
        
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

if __name__ == "__main__":
    main()
