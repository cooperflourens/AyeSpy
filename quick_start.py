#!/usr/bin/env python3
"""
AyeSpy Quick Start Script
Provides an easy way to get AyeSpy running quickly.
"""

import os
import sys
import subprocess
import time
from typing import Dict, Any

def print_header():
    """Print welcome header."""
    print("🏛️  " + "=" * 48)
    print("🏛️   AyeSpy Congressional Transparency Platform")
    print("🏛️  " + "=" * 48)
    print("🏛️   Quick Start Guide")
    print("🏛️  " + "=" * 48)

def check_python_version() -> bool:
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_environment() -> Dict[str, bool]:
    """Check if we're in the right environment."""
    checks = {}
    
    # Check if we're in conda environment
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'Not in conda')
    if conda_env == 'SEEK':
        print(f"✅ Conda environment: {conda_env}")
        checks['conda'] = True
    else:
        print(f"⚠️  Conda environment: {conda_env} (expected: SEEK)")
        checks['conda'] = False
    
    # Check if key files exist
    key_files = ['ui.py', 'main.py', 'environment.yml']
    for file in key_files:
        if os.path.exists(file):
            print(f"✅ Found: {file}")
            checks[file] = True
        else:
            print(f"❌ Missing: {file}")
            checks[file] = False
    
    return checks

def run_system_test() -> bool:
    """Run the system test script."""
    try:
        print("\n🧪 Running system tests...")
        result = subprocess.run([sys.executable, 'test_system.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ System tests passed!")
            return True
        else:
            print("❌ System tests failed!")
            print("STDOUT:", result.stdout[-500:] if result.stdout else "None")
            print("STDERR:", result.stderr[-500:] if result.stderr else "None")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  System tests timed out (may be downloading models)")
        return False
    except Exception as e:
        print(f"❌ Could not run system tests: {e}")
        return False

def initialize_database() -> bool:
    """Initialize the database."""
    try:
        print("\n💾 Initializing database...")
        result = subprocess.run([sys.executable, 'init_database.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Database initialized!")
            return True
        else:
            print("⚠️  Database initialization had issues:")
            if result.stdout:
                print(result.stdout[-300:])
            if result.stderr:
                print("Errors:", result.stderr[-300:])
            return False
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def start_web_ui() -> bool:
    """Start the web UI in a separate process."""
    try:
        print("\n🌐 Starting web UI...")
        print("   Web UI will be available at: http://localhost:5000")
        print("   Press Ctrl+C to stop")
        
        # Start Flask app
        subprocess.run([sys.executable, 'ui.py'])
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Web UI stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start web UI: {e}")
        return False

def start_terminal_app() -> bool:
    """Start the terminal application."""
    try:
        print("\n💻 Starting terminal application...")
        subprocess.run([sys.executable, 'main.py'])
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Terminal app stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start terminal app: {e}")
        return False

def show_menu() -> str:
    """Show main menu and get user choice."""
    print("\n📋 What would you like to do?")
    print("   1. 🧪 Run system tests")
    print("   2. 💾 Initialize database") 
    print("   3. 🌐 Start web UI")
    print("   4. 💻 Start terminal app")
    print("   5. 📖 View setup instructions")
    print("   6. 🚪 Exit")
    
    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice
        print("Invalid choice. Please enter 1-6.")

def show_setup_instructions():
    """Show setup instructions."""
    print("\n📖 SETUP INSTRUCTIONS")
    print("-" * 50)
    
    if os.path.exists('SETUP_INSTRUCTIONS.md'):
        print("Detailed instructions are available in: SETUP_INSTRUCTIONS.md")
        print("\nKey steps:")
        print("1. Install dependencies:  conda env create -f environment.yml")
        print("2. Activate environment:  conda activate SEEK")
        print("3. Setup PostgreSQL:      See SETUP_INSTRUCTIONS.md")
        print("4. Run this script:       python quick_start.py")
    else:
        print("❌ SETUP_INSTRUCTIONS.md not found")
        print("\nBasic setup:")
        print("1. conda env create -f environment.yml")
        print("2. conda activate SEEK")
        print("3. pip install -r requirements.txt")
        print("4. Setup PostgreSQL database")

def main():
    """Main function."""
    print_header()
    
    # Basic checks
    if not check_python_version():
        return False
    
    checks = check_environment()
    
    # Interactive menu
    while True:
        choice = show_menu()
        
        if choice == '1':
            run_system_test()
            
        elif choice == '2':
            initialize_database()
            
        elif choice == '3':
            start_web_ui()
            
        elif choice == '4':
            start_terminal_app()
            
        elif choice == '5':
            show_setup_instructions()
            
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
