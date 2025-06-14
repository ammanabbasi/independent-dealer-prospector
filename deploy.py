#!/usr/bin/env python3
"""
🚀 Independent Dealer Prospector - Deployment Helper
"""

import subprocess
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if all required files exist for deployment."""
    required_files = [
        "app.py",
        "requirements.txt", 
        ".streamlit/config.toml",
        "README.md",
        "DEPLOYMENT.md",
        "secrets.toml.template"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    return True

def check_git_repo():
    """Check if this is a git repository."""
    try:
        subprocess.run(["git", "status"], check=True, capture_output=True)
        print("✅ Git repository detected")
        return True
    except subprocess.CalledProcessError:
        print("❌ Not a git repository. Initialize with: git init")
        return False

def check_secrets():
    """Check if secrets.toml exists and warn user."""
    secrets_path = Path(".streamlit/secrets.toml")
    
    if secrets_path.exists():
        print("⚠️  Found .streamlit/secrets.toml")
        print("   Make sure this file contains your actual API keys")
        print("   This file will NOT be deployed (it's in .gitignore)")
        return True
    else:
        print("❌ No .streamlit/secrets.toml found")
        print("   Copy secrets.toml.template to .streamlit/secrets.toml")
        print("   Add your actual API keys to the copied file")
        return False

def display_deployment_options():
    """Display deployment options."""
    print("\n🚀 DEPLOYMENT OPTIONS:")
    print("\n1️⃣  STREAMLIT COMMUNITY CLOUD (Recommended)")
    print("   • Free hosting for public repositories")
    print("   • Official Streamlit platform")
    print("   • Easy setup and management")
    print("   → Visit: https://share.streamlit.io")
    
    print("\n2️⃣  RAILWAY")
    print("   • Modern deployment platform")
    print("   • Simple GitHub integration")
    print("   → Visit: https://railway.app")
    
    print("\n3️⃣  RENDER")
    print("   • Free tier available")
    print("   • Automatic deploys")
    print("   → Visit: https://render.com")
    
    print("\n4️⃣  HEROKU")
    print("   • Classic platform")
    print("   • Wide ecosystem")
    print("   → Visit: https://heroku.com")

def prepare_git():
    """Prepare git repository for deployment."""
    try:
        # Check if there are uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("\n📝 Uncommitted changes detected:")
            print(result.stdout)
            
            commit = input("\n💾 Commit changes for deployment? (y/n): ").lower().strip()
            if commit == 'y':
                subprocess.run(["git", "add", "."])
                commit_msg = input("📝 Enter commit message (or press Enter for default): ").strip()
                if not commit_msg:
                    commit_msg = "Ready for deployment - Independent Dealer Prospector"
                
                subprocess.run(["git", "commit", "-m", commit_msg])
                print("✅ Changes committed")
        
        # Check if remote exists
        result = subprocess.run(["git", "remote", "-v"], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("\n❌ No git remote found")
            print("   Add your GitHub repository:")
            print("   git remote add origin https://github.com/username/repository.git")
            return False
        
        print("✅ Git repository ready for deployment")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False

def open_deployment_links():
    """Open deployment platform links."""
    choice = input("\n🌐 Open deployment platform? (1-4 or 'n' for none): ").strip()
    
    urls = {
        '1': 'https://share.streamlit.io',
        '2': 'https://railway.app',
        '3': 'https://render.com', 
        '4': 'https://heroku.com'
    }
    
    if choice in urls:
        print(f"🌐 Opening {urls[choice]}...")
        webbrowser.open(urls[choice])

def main():
    """Main deployment helper function."""
    print("🎯 INDEPENDENT DEALER PROSPECTOR - DEPLOYMENT HELPER")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Fix missing files before deployment")
        return
    
    # Check git
    if not check_git_repo():
        print("\n❌ Initialize git repository first")
        return
    
    # Check secrets
    if not check_secrets():
        print("\n❌ Configure secrets before deployment")
        return
    
    # Prepare git
    if not prepare_git():
        print("\n❌ Fix git issues before deployment")
        return
    
    # Display options
    display_deployment_options()
    
    # Show next steps
    print("\n📋 NEXT STEPS:")
    print("1. Push your code to GitHub (if not already done)")
    print("2. Choose a deployment platform above")
    print("3. Create new app and connect your repository")
    print("4. Add your API keys in the platform's secrets/environment variables")
    print("5. Deploy and test your live app!")
    
    print("\n📖 See DEPLOYMENT.md for detailed instructions")
    
    # Open deployment platform
    open_deployment_links()
    
    print("\n🎉 Your Independent Dealer Prospector is ready to go live!")
    print("   Need help? Check DEPLOYMENT.md or create a GitHub issue")

if __name__ == "__main__":
    main() 