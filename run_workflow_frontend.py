"""
Workflow frontend launcher for Healthcare Planning Assistant
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
    """Launch the workflow frontend with complete process"""
    print("🖥️  Starting Healthcare Workflow Frontend...")
    print("🌐 Frontend will be available at: http://localhost:8505")
    print("🔥 This implements the complete healthcare workflow process")
    print("📋 Steps: Authentication → Data Collection → AI Processing → Recommendations → Follow-up")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_script = os.path.join(project_dir, "frontend", "workflow_app.py")
        if not os.path.exists(frontend_script):
            print("❌ Error: frontend/workflow_app.py not found. Please run from the project directory.")
            return
        
        py_exe = get_python_executable()
        os.chdir(os.path.join(project_dir, "frontend"))
        subprocess.run([py_exe, "-m", "streamlit", "run", "workflow_app.py", "--server.port", "8505"])
        
    except KeyboardInterrupt:
        print("\n👋 Workflow frontend server stopped by user")
    except Exception as e:
        print(f"❌ Error starting workflow frontend: {e}")

if __name__ == "__main__":
    main()
