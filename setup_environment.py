#!/usr/bin/env python3
"""
Environment Setup Script for Independent Dealer Prospector CRM
Helps initialize the database and verify all dependencies are working.
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def setup_secrets():
    """Create secrets file from template if it doesn't exist."""
    secrets_dir = Path(".streamlit")
    secrets_file = secrets_dir / "secrets.toml"
    template_file = Path("secrets.toml.template")
    
    if not secrets_dir.exists():
        secrets_dir.mkdir()
        print("📁 Created .streamlit directory")
    
    if not secrets_file.exists() and template_file.exists():
        # Copy template to secrets.toml
        with open(template_file, 'r') as src, open(secrets_file, 'w') as dst:
            dst.write(src.read())
        print("🔑 Created .streamlit/secrets.toml from template")
        print("⚠️  Please edit .streamlit/secrets.toml with your actual API keys!")
        return False
    elif secrets_file.exists():
        print("✅ Secrets file already exists")
        return True
    else:
        print("❌ No secrets template found")
        return False

def setup_database():
    """Initialize the CRM database."""
    print("🗄️  Setting up CRM database...")
    try:
        # Import here to ensure dependencies are installed
        from models.database import get_db_manager
        
        db_manager = get_db_manager()
        db_manager.create_tables()
        
        print("✅ CRM database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to setup database: {e}")
        return False

def verify_imports():
    """Verify all critical imports work."""
    print("🔍 Verifying imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported")
        
        from models.database import get_db_manager
        print("✅ Database models imported")
        
        from services.crm_service import crm_service
        print("✅ CRM service imported")
        
        from services.communication_service import communication_service
        print("✅ Communication service imported")
        
        from components.crm_ui import render_enhanced_prospect_card
        print("✅ UI components imported")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def run_basic_tests():
    """Run basic functionality tests."""
    print("🧪 Running basic tests...")
    try:
        # Run the test file
        result = subprocess.run([sys.executable, "tests/test_crm.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Basic tests passed")
            return True
        else:
            print(f"❌ Tests failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Could not run tests: {e}")
        return False

def main():
    """Main setup routine."""
    print("🎯 Independent Dealer Prospector CRM - Environment Setup")
    print("=" * 60)
    
    success = True
    
    # Step 1: Install dependencies
    if not install_dependencies():
        success = False
    
    # Step 2: Setup secrets
    secrets_ready = setup_secrets()
    if not secrets_ready:
        print("⚠️  You need to configure your API keys before continuing.")
        print("   Edit .streamlit/secrets.toml with your actual keys.")
    
    # Step 3: Verify imports
    if not verify_imports():
        success = False
    
    # Step 4: Setup database
    if not setup_database():
        success = False
    
    # Step 5: Run tests
    if not run_basic_tests():
        success = False
    
    print("\n" + "=" * 60)
    if success and secrets_ready:
        print("🎉 Setup completed successfully!")
        print("\n🚀 You can now run the application with:")
        print("   streamlit run app.py")
    elif success:
        print("⚠️  Setup mostly completed!")
        print("   Please configure your API keys in .streamlit/secrets.toml")
        print("   Then run: streamlit run app.py")
    else:
        print("❌ Setup encountered errors. Please check the output above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 