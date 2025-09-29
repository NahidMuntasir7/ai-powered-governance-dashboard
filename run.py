"""
Main runner script for the Civic Feedback Platform
HackTheAI 2025 Project
"""

import subprocess
import sys
import os


def run_application():
    """Run the Streamlit application"""
    
    # Check if database exists, if not run setup
    if not os.path.exists('civic_governance.db'):
        print("🔧 Database not found. Running setup...")
        from setup import setup_project
        setup_project()
    
    print("🚀 Starting Civic Feedback Platform...")
    print("📱 Open your browser and go to: http://localhost:8501")
    print("⭐ Press Ctrl+C to stop the server")
    
    # Run Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "main_app.py"])

if __name__ == "__main__":
    run_application()