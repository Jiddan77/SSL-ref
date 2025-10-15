#!/usr/bin/env python3
"""
Setup script for SSL Referee Bias Analysis System
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def setup_virtual_environment():
    """Set up virtual environment if it doesn't exist"""
    if not os.path.exists('venv'):
        print("🔧 Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'])
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:  # macOS/Linux
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    try:
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def check_chrome():
    """Check if Chrome is available for Selenium"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['where', 'chrome'], check=True, capture_output=True)
        else:  # macOS/Linux
            subprocess.run(['which', 'google-chrome'], check=True, capture_output=True)
        print("✅ Chrome browser detected")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Chrome browser not found - required for web scraping")
        print("Please install Google Chrome from https://www.google.com/chrome/")
        return False

def create_sample_config():
    """Create sample configuration if it doesn't exist"""
    if not os.path.exists('ssl_api_solution.json'):
        print("📝 Creating sample configuration...")
        sample_config = {
            "description": "SSL API configuration - needs to be refreshed",
            "status": "needs_refresh",
            "instructions": "Run ssl_smart_scraper.py to automatically obtain fresh API tokens"
        }
        
        with open('ssl_api_solution.json', 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        print("✅ Sample configuration created")

def main():
    """Main setup process"""
    print("🏒 SSL Referee Bias Analysis System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Setup virtual environment
    setup_virtual_environment()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check Chrome
    chrome_ok = check_chrome()
    
    # Create sample config
    create_sample_config()
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("2. Run the smart scraper:")
    print("   python ssl_smart_scraper.py")
    
    if not chrome_ok:
        print("\n⚠️ Note: Install Chrome browser for full functionality")
    
    print("\n📖 Read README.md for detailed usage instructions")
    print("🤝 See CONTRIBUTING.md to help improve the project")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)