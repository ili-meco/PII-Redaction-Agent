#!/usr/bin/env python3
"""
setup_checker.py
================
Pre-workshop setup verification script

This script helps participants verify their environment is ready before the workshop.
Run this first to catch any setup issues early.

Usage: python setup_checker.py
"""

import os
import sys
import json
import subprocess
from typing import List, Tuple, Dict

class SetupChecker:
    def __init__(self):
        self.checks_passed = 0
        self.checks_total = 0
        self.issues = []
        
    def check_item(self, description: str, check_func, fix_suggestion: str = None) -> bool:
        """Run a single check and report results"""
        self.checks_total += 1
        print(f"🔍 Checking: {description}...", end=" ")
        
        try:
            result = check_func()
            if result:
                print("✅ PASS")
                self.checks_passed += 1
                return True
            else:
                print("❌ FAIL")
                if fix_suggestion:
                    self.issues.append(f"❌ {description}: {fix_suggestion}")
                return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.issues.append(f"❌ {description}: {str(e)}")
            return False
    
    def check_python_version(self) -> bool:
        """Check Python version is 3.8+"""
        version = sys.version_info
        return version.major == 3 and version.minor >= 8
    
    def check_pip_available(self) -> bool:
        """Check if pip is available"""
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         capture_output=True, check=True, timeout=10)
            return True
        except:
            return False
    
    def check_required_packages(self) -> bool:
        """Check if required packages are installed"""
        required_packages = ["requests"]
        
        try:
            for package in required_packages:
                __import__(package)
            return True
        except ImportError:
            return False
    
    def check_workspace_structure(self) -> bool:
        """Check if the workspace has the expected structure"""
        required_paths = [
            "results/pii_detection/src/pii_redaction_agent.py",
            "results/pii_detection/src/demo_pii_redaction.py", 
            "results/pii_detection/src/env_loader.py",
            "data/images/receipt.png",
            "config"
        ]
        
        for path in required_paths:
            if not os.path.exists(path):
                return False
        return True
    
    def check_config_exists(self) -> bool:
        """Check if config file exists"""
        return os.path.exists("config/.env")
    
    def check_config_completeness(self) -> bool:
        """Check if config has required values"""
        if not os.path.exists("config/.env"):
            return False
            
        try:
            # Add path for env_loader
            sys.path.append('results/pii_detection/src')
            from env_loader import load_dotenv
            
            load_dotenv("config/.env")
            
            required_vars = [
                'AZURE_OPENAI_ENDPOINT',
                'AZURE_OPENAI_KEY',
                'AZURE_OPENAI_DEPLOYMENT', 
                'AZURE_DOCINTEL_ENDPOINT',
                'AZURE_DOCINTEL_KEY'
            ]
            
            for var in required_vars:
                value = os.getenv(var)
                if not value or value.strip() == "" or "your-" in value.lower():
                    return False
            return True
        except:
            return False
    
    def check_sample_files(self) -> bool:
        """Check if sample files are present"""
        sample_files = [
            "data/images/receipt.png",
            "data/images/driverslicense.jpg"
        ]
        
        for file_path in sample_files:
            if not os.path.exists(file_path):
                return False
        return True
    
    def check_write_permissions(self) -> bool:
        """Check write permissions in output directories"""
        test_dirs = [
            "results/pii_detection/redacted_text",
            "results/pii_detection/reports"
        ]
        
        for dir_path in test_dirs:
            os.makedirs(dir_path, exist_ok=True)
            test_file = os.path.join(dir_path, "test_write.tmp")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except:
                return False
        return True
    
    def run_full_check(self):
        """Run all setup checks"""
        print("🔧 PII Redaction Agent - Setup Verification")
        print("=" * 50)
        print()
        
        # Core Python environment
        print("📋 PYTHON ENVIRONMENT:")
        self.check_item(
            "Python 3.8+", 
            self.check_python_version,
            "Please install Python 3.8 or higher"
        )
        
        self.check_item(
            "pip package manager", 
            self.check_pip_available,
            "Please install pip or use python -m ensurepip"
        )
        
        # Dependencies
        print("\n📦 PYTHON PACKAGES:")
        self.check_item(
            "Required packages (requests)", 
            self.check_required_packages,
            "Run: pip install -r requirements.txt"
        )
        
        # Workspace structure
        print("\n📁 WORKSPACE STRUCTURE:")
        self.check_item(
            "Project files and directories", 
            self.check_workspace_structure,
            "Ensure you've cloned the complete repository"
        )
        
        self.check_item(
            "Sample data files", 
            self.check_sample_files,
            "Check data/images/ directory for sample files"
        )
        
        self.check_item(
            "Write permissions", 
            self.check_write_permissions,
            "Ensure you can write to output directories"
        )
        
        # Configuration
        print("\n⚙️ AZURE CONFIGURATION:")
        self.check_item(
            "Config file exists", 
            self.check_config_exists,
            "Create config/.env file with your Azure credentials"
        )
        
        self.check_item(
            "Config file completeness", 
            self.check_config_completeness,
            "Fill in your Azure service endpoints and API keys in config/.env"
        )
        
        # Summary
        self.print_summary()
        
    def print_summary(self):
        """Print setup verification summary"""
        print("\n" + "=" * 50)
        print("📊 SETUP VERIFICATION SUMMARY")
        print("=" * 50)
        
        success_rate = (self.checks_passed / self.checks_total) * 100
        
        print(f"✅ Checks passed: {self.checks_passed}/{self.checks_total} ({success_rate:.0f}%)")
        
        if self.checks_passed == self.checks_total:
            print("\n🎉 EXCELLENT! Your environment is ready for the workshop!")
            print("\nNext steps:")
            print("1. Run: python workshop_walkthrough.py")
            print("2. Follow the interactive guide")
            print("3. Enjoy learning about PII detection!")
            
        else:
            print(f"\n⚠️  SETUP INCOMPLETE: {len(self.issues)} issues need attention")
            print("\nIssues to fix:")
            for issue in self.issues:
                print(f"  {issue}")
                
            print("\nRecommended actions:")
            print("1. Fix the issues listed above")
            print("2. Run this setup checker again")
            print("3. Proceed to workshop when all checks pass")
            
        print("\n" + "=" * 50)
        
    def quick_setup_guide(self):
        """Show quick setup commands"""
        print("\n🚀 QUICK SETUP GUIDE:")
        print("-" * 30)
        print()
        print("1. Install dependencies:")
        print("   pip install -r requirements.txt")
        print()
        print("2. Create config file:")
        print("   cp .env.template config/.env")
        print("   # Edit config/.env with your Azure credentials")
        print()
        print("3. Verify setup:")
        print("   python setup_checker.py")
        print()
        print("4. Start workshop:")
        print("   python workshop_walkthrough.py")

def main():
    """Main setup checker entry point"""
    checker = SetupChecker()
    
    # Show quick guide if requested
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', '--guide']:
        checker.quick_setup_guide()
        return
    
    # Run full check
    try:
        checker.run_full_check()
    except KeyboardInterrupt:
        print("\n\n👋 Setup check interrupted.")
    except Exception as e:
        print(f"\n❌ Setup check error: {e}")
        print("Please check your environment and try again.")

if __name__ == "__main__":
    main()
