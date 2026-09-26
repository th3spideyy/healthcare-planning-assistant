"""
Simple launcher for Healthcare Planning Assistant GUI
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
    """Launch the Healthcare Planning Assistant GUI"""
    print("🏥 Starting Healthcare Planning Assistant GUI...")
    
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        gui_script = os.path.join(project_dir, "gui_app.py")
        if not os.path.exists(gui_script):
            print("❌ Error: gui_app.py not found. Please run from the project directory.")
            return
        
        py_exe = get_python_executable()
        subprocess.run([py_exe, gui_script])
        
    except KeyboardInterrupt:
        print("\n👋 GUI closed by user")
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")

if __name__ == "__main__":
    main()
