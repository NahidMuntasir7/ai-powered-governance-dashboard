"""
Setup script for the AI-Powered Civic Feedback & Governance Platform
HackTheAI 2025 Project
"""

import os
import sys
from sample_data import create_sample_data

def setup_project():
    """Set up the project for first-time use"""
    print("🏛️ Setting up AI-Powered Civic Feedback & Governance Platform")
    print("=" * 60)
    
    # Create directories
    os.makedirs("reports", exist_ok=True)
    os.makedirs(".streamlit", exist_ok=True)
    
    # Create .env file template
    # if not os.path.exists('.env'):
    #     with open('.env', 'w') as f:
    #         f.write("# Google Gemini API Key (Get from https://makersuite.google.com/app/apikey)\n")
    #         f.write("GOOGLE_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n")
    #     print("✅ Created .env file template")
    
    # Create Streamlit config
    config_content = """
[theme]
primaryColor = "#3b82f6"
backgroundColor = "#000000"
secondaryBackgroundColor = "#111111"
textColor = "#ffffff"

[server]
headless = true
port = 8501
"""
    
    with open('.streamlit/config.toml', 'w') as f:
        f.write(config_content)
    print("✅ Created Streamlit configuration")
    
    # Create sample data
    print("\n📊 Creating sample data...")
    create_sample_data()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Add your Google Gemini API key to .env file")
    print("2. Run: streamlit run main_app.py")
    print("3. Demo credentials:")
    print("   👤 Citizen: ahmed@email.com / password123")
    print("   👨‍💼 Admin: admin@gov.bd / admin123")

if __name__ == "__main__":
    setup_project()