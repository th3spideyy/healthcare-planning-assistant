"""
Workflow backend launcher for Healthcare Planning Assistant
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
    """Launch the workflow backend server"""
    print("🚀 Starting Healthcare Workflow Backend...")
    print("📍 API will be available at: http://localhost:8003")
    print("📚 API Documentation: http://localhost:8003/docs")
    print("🔥 This implements the complete healthcare workflow process")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        api_script = os.path.join(project_dir, "api", "workflow_api.py")
        if not os.path.exists(api_script):
            print("❌ Error: api/workflow_api.py not found. Please run from the project directory.")
            return
        
        py_exe = get_python_executable()
        os.chdir(os.path.join(project_dir, "api"))
        subprocess.run([py_exe, "workflow_api.py"])
        
    except KeyboardInterrupt:
        print("\n👋 Workflow backend server stopped by user")
    except Exception as e:
        print(f"❌ Error starting workflow backend: {e}")

if __name__ == "__main__":
    main()
