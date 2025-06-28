#!/usr/bin/env python3
"""
Setup script for Health Checkup Analyzer
This script helps users install dependencies and check system requirements.
"""

import subprocess
import sys
import os
import platform

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def check_pip():
    """Check if pip is available"""
    success, _, _ = run_command("pip --version")
    if success:
        print("✅ pip - OK")
        return True
    else:
        print("❌ pip not found")
        return False

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python dependencies...")
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    if success:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False

def check_tesseract():
    """Check if Tesseract is installed"""
    success, stdout, stderr = run_command("tesseract --version")
    if success:
        print("✅ Tesseract OCR - OK")
        return True
    else:
        print("❌ Tesseract OCR not found")
        return False

def install_tesseract_guide():
    """Provide instructions for installing Tesseract"""
    system = platform.system().lower()
    
    print("\n🔧 Tesseract Installation Guide:")
    print("=" * 50)
    
    if system == "darwin":  # macOS
        print("For macOS:")
        print("brew install tesseract")
        print("\nIf you don't have Homebrew:")
        print("1. Install Homebrew: https://brew.sh/")
        print("2. Then run: brew install tesseract")
        
    elif system == "linux":
        print("For Ubuntu/Debian:")
        print("sudo apt-get update")
        print("sudo apt-get install tesseract-ocr")
        print("sudo apt-get install libtesseract-dev")
        
        print("\nFor CentOS/RHEL:")
        print("sudo yum install tesseract")
        
    elif system == "windows":
        print("For Windows:")
        print("1. Download Tesseract from:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install the executable")
        print("3. Add Tesseract to your PATH environment variable")
        
    else:
        print("Please install Tesseract OCR for your operating system")
        print("Visit: https://tesseract-ocr.github.io/tessdoc/Installation.html")

def main():
    """Main setup function"""
    print("🏥 Health Checkup Analyzer - Setup")
    print("=" * 40)
    
    # Check system requirements
    print("\n🔍 Checking system requirements...")
    
    requirements_met = True
    
    # Check Python version
    if not check_python_version():
        requirements_met = False
    
    # Check pip
    if not check_pip():
        requirements_met = False
    
    # Check Tesseract
    tesseract_ok = check_tesseract()
    if not tesseract_ok:
        requirements_met = False
        install_tesseract_guide()
    
    if not requirements_met:
        print("\n❌ Please fix the above issues before continuing")
        return False
    
    # Install Python dependencies
    if os.path.exists("requirements.txt"):
        install_success = install_requirements()
        if not install_success:
            return False
    else:
        print("❌ requirements.txt not found")
        return False
    
    # Final success message
    print("\n🎉 Setup completed successfully!")
    print("\n🚀 To run the application:")
    print("streamlit run healthcheckapp.py")
    print("\n📖 For detailed instructions, see README.md")
    print("\n⚠️  Don't forget to:")
    print("1. Get your OpenAI API key from: https://platform.openai.com/api-keys")
    print("2. Enter the API key in the app sidebar")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1) 