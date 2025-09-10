#!/usr/bin/env python3
"""
setup.py
Workshop setup script to verify environment and configuration
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['requests', 'azure.cognitiveservices.speech']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'azure.cognitiveservices.speech':
                import azure.cognitiveservices.speech
                print("✅ azure-cognitiveservices-speech is installed")
            else:
                __import__(package)
                print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\nTo install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_directory_structure():
    """Verify the expected directory structure exists"""
    required_dirs = [
        'config',
        'data/audio',
        'data/documents', 
        'data/images',
        'results/pii_detection/src',
        'results/pii_detection/tests',
        'results/pii_detection/redacted_text',
        'results/pii_detection/reports',
        'src'
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Missing directory: {dir_path}")
            return False
        print(f"✅ Directory exists: {dir_path}")
    
    return True

def check_sample_files():
    """Check if sample files are present"""
    sample_files = [
        'data/documents/sample_document_with_pii.txt',
        'data/images/receipt.png',
        'data/images/driverslicense.jpg'
    ]
    
    for file_path in sample_files:
        if Path(file_path).exists():
            print(f"✅ Sample file exists: {file_path}")
        else:
            print(f"⚠️ Sample file missing: {file_path}")
    
    return True

def check_config_file():
    """Check if configuration file exists"""
    config_file = Path('config/.env')
    template_file = Path('.env.template')
    
    if not config_file.exists():
        if template_file.exists():
            print("⚠️ Configuration file missing. Please create config/.env from .env.template")
            print("Run: cp .env.template config/.env")
            print("Then edit config/.env with your Azure credentials")
        else:
            print("❌ Both config/.env and .env.template are missing")
        return False
    else:
        print("✅ Configuration file exists: config/.env")
        
        # Check if it contains actual values (not just template placeholders)
        with open(config_file, 'r') as f:
            content = f.read()
            if 'your-endpoint' in content or 'your-key' in content:
                print("⚠️ Configuration file contains template placeholders")
                print("Please edit config/.env with your actual Azure credentials")
                return False
        
        print("✅ Configuration file appears to be configured")
        return True

def main():
    """Main setup verification function"""
    print("🔧 PII Redaction Workshop Setup Verification")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 5
    
    # Run all checks
    if check_python_version():
        checks_passed += 1
    
    if check_dependencies():
        checks_passed += 1
    
    if check_directory_structure():
        checks_passed += 1
        
    if check_sample_files():
        checks_passed += 1
    
    if check_config_file():
        checks_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Setup verification complete: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 Setup is complete! You're ready for the workshop.")
        print("\nNext steps:")
        print("1. cd results/pii_detection/src")
        print("2. python demo_pii_redaction.py")
    else:
        print("❌ Setup incomplete. Please address the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
