"""
Streamlit configuration helper
Creates the required .streamlit directory and secrets.toml file
"""

import os
from pathlib import Path

def setup_streamlit_config():
    """Set up Streamlit configuration directory and files"""
    
    # Get the app directory
    app_dir = Path(__file__).parent
    streamlit_dir = app_dir / ".streamlit"
    
    # Create .streamlit directory if it doesn't exist
    streamlit_dir.mkdir(exist_ok=True)
    
    # Create secrets.toml if it doesn't exist
    secrets_file = streamlit_dir / "secrets.toml"
    
    if not secrets_file.exists():
        secrets_content = '''# Streamlit Secrets Configuration
# Add your actual API keys here - this file is gitignored for security

# Google Maps API Key (required for core functionality)
GOOGLE_MAPS_API_KEY = "your-google-maps-api-key-here"

# OpenAI API Key (required for AI sales intelligence)
OPENAI_API_KEY = "your-openai-api-key-here"

# CRM Database Configuration
DATABASE_URL = "sqlite:///crm_data.db"

# Communication Services (optional)
TWILIO_ACCOUNT_SID = "your-twilio-account-sid"
TWILIO_AUTH_TOKEN = "your-twilio-auth-token" 
TWILIO_PHONE_NUMBER = "your-twilio-phone-number"

SENDGRID_API_KEY = "your-sendgrid-api-key"
FROM_EMAIL = "sales@yourdomain.com"
FROM_NAME = "Sales Team"

# App Configuration
SUPPORT_EMAIL = "support@yourdomain.com"
CONTACT_INFO = "Your Contact Information"
'''
        
        with open(secrets_file, 'w') as f:
            f.write(secrets_content)
        
        print(f"Created {secrets_file}")
        print("Please edit the file and add your actual API keys!")
    else:
        print(f"Configuration file {secrets_file} already exists")
    
    # Create config.toml for Streamlit settings
    config_file = streamlit_dir / "config.toml"
    
    if not config_file.exists():
        config_content = '''[global]
developmentMode = false

[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
'''
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print(f"Created {config_file}")

if __name__ == "__main__":
    setup_streamlit_config()