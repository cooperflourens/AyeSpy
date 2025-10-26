#!/usr/bin/env python3
"""
Windows-specific setup script for AyeSpy.
Handles conda environment issues and provides alternative setup methods.
"""

import os
import sys
import subprocess
import platform
from typing import List, Tuple

def print_header():
    """Print setup header."""
    print("🏛️  AyeSpy Windows Setup")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 50)

def check_conda() -> bool:
    """Check if conda is available."""
    try:
        result = subprocess.run(['conda', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Conda found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Conda not found")
            return False
    except FileNotFoundError:
        print("❌ Conda not found in PATH")
        return False

def create_environment_simple() -> Tuple[bool, str]:
    """Create conda environment with simplified approach."""
    try:
        print("🔧 Creating conda environment with basic packages...")
        
        # Method 1: Try the Windows-specific environment file
        if os.path.exists('environment-windows.yml'):
            print("   Using environment-windows.yml...")
            result = subprocess.run([
                'conda', 'env', 'create', '-f', 'environment-windows.yml'
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return True, "Created environment from environment-windows.yml"
            else:
                print(f"   ⚠️  environment-windows.yml failed: {result.stderr}")
        
        # Method 2: Create environment manually with basic packages
        print("   Creating environment with basic packages...")
        
        # Create basic environment
        result = subprocess.run([
            'conda', 'create', '-n', 'AyeSpy', 'python=3.12', '-y'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return False, f"Failed to create basic environment: {result.stderr}"
        
        # Install packages one by one
        basic_packages = [
            'numpy', 'pandas', 'requests', 'pip', 'jupyter'
        ]
        
        for package in basic_packages:
            print(f"   Installing {package}...")
            result = subprocess.run([
                'conda', 'install', '-n', 'AyeSpy', package, '-y'
            ], capture_output=True, text=True, timeout=180)
            
            if result.returncode != 0:
                print(f"   ⚠️  Failed to install {package}")
        
        return True, "Created basic environment successfully"
        
    except subprocess.TimeoutExpired:
        return False, "Environment creation timed out"
    except Exception as e:
        return False, f"Environment creation failed: {e}"

def install_pip_packages() -> Tuple[bool, str]:
    """Install Python packages via pip in the AyeSpy environment."""
    try:
        print("📦 Installing Python packages via pip...")
        
        # Determine the correct python executable
        if platform.system() == "Windows":
            python_exe = os.path.expanduser("~/miniconda3/envs/AyeSpy/python.exe")
            if not os.path.exists(python_exe):
                python_exe = os.path.expanduser("~/anaconda3/envs/AyeSpy/python.exe")
        else:
            python_exe = "python"
        
        # Core packages
        core_packages = [
            'flask==2.3.3',
            'sqlalchemy==2.0.23', 
            'psycopg2-binary==2.9.9',
            'transformers==4.35.0',
            'torch',
            'rich==13.6.0',
            'python-dotenv==1.0.0',
            'beautifulsoup4==4.12.2',
            'sentence-transformers==2.2.2'
        ]
        
        for package in core_packages:
            print(f"   Installing {package}...")
            try:
                if os.path.exists(python_exe):
                    result = subprocess.run([
                        python_exe, '-m', 'pip', 'install', package
                    ], capture_output=True, text=True, timeout=300)
                else:
                    # Fallback to conda run
                    result = subprocess.run([
                        'conda', 'run', '-n', 'AyeSpy', 'pip', 'install', package
                    ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"   ✅ {package}")
                else:
                    print(f"   ⚠️  {package} - {result.stderr.strip()}")
                    
            except subprocess.TimeoutExpired:
                print(f"   ⚠️  {package} - installation timed out")
            except Exception as e:
                print(f"   ⚠️  {package} - {e}")
        
        return True, "Pip packages installed"
        
    except Exception as e:
        return False, f"Pip installation failed: {e}"

def use_requirements_txt() -> Tuple[bool, str]:
    """Install from requirements.txt as fallback."""
    try:
        print("📋 Installing from requirements.txt...")
        
        if not os.path.exists('requirements.txt'):
            print("   ❌ requirements.txt not found")
            return False, "requirements.txt missing"
        
        # Try conda run first
        result = subprocess.run([
            'conda', 'run', '-n', 'AyeSpy', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            return True, "Installed from requirements.txt"
        else:
            print(f"   ⚠️  Some packages may have failed: {result.stderr}")
            return True, "Partial installation from requirements.txt"
            
    except Exception as e:
        return False, f"Requirements installation failed: {e}"

def test_installation() -> Tuple[bool, List[str]]:
    """Test the installation."""
    print("🧪 Testing installation...")
    
    test_imports = [
        'import flask; print("Flask OK")',
        'import pandas; print("Pandas OK")', 
        'import numpy; print("NumPy OK")',
        'import requests; print("Requests OK")',
        'import rich; print("Rich OK")'
    ]
    
    results = []
    success_count = 0
    
    for test_code in test_imports:
        try:
            result = subprocess.run([
                'conda', 'run', '-n', 'AyeSpy', 'python', '-c', test_code
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"   ✅ {result.stdout.strip()}")
                success_count += 1
            else:
                print(f"   ❌ Import test failed")
                
        except Exception as e:
            print(f"   ❌ Test error: {e}")
    
    results.append(f"✅ {success_count}/{len(test_imports)} core packages working")
    
    # Test AI packages (optional)
    ai_tests = [
        'import torch; print("PyTorch OK")',
        'import transformers; print("Transformers OK")'
    ]
    
    ai_success = 0
    for test_code in ai_tests:
        try:
            result = subprocess.run([
                'conda', 'run', '-n', 'AyeSpy', 'python', '-c', test_code
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"   ✅ {result.stdout.strip()}")
                ai_success += 1
            else:
                print(f"   ⚠️  AI package test failed (may need manual install)")
                
        except Exception as e:
            print(f"   ⚠️  AI test error: {e}")
    
    results.append(f"✅ {ai_success}/{len(ai_tests)} AI packages working")
    
    return success_count >= 4, results

def show_next_steps():
    """Show next steps after setup."""
    print("\n" + "=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("=" * 50)
    
    print("\n📋 Next steps:")
    print("1. Activate environment:")
    print("   conda activate AyeSpy")
    print()
    print("2. Test the system:")
    print("   python test_system.py")
    print()
    print("3. Start AyeSpy:")
    print("   python ui.py          # Web interface")
    print("   python main.py        # Terminal app")
    print("   python quick_start.py # Interactive menu")
    
    print("\n⚠️  If you get import errors:")
    print("   conda activate AyeSpy")
    print("   pip install flask rich transformers torch")
    
    print("\n📖 For detailed help:")
    print("   See START_HERE.md")

def main():
    """Main setup function."""
    print_header()
    
    # Check conda
    if not check_conda():
        print("\n❌ Conda is required. Please install Miniconda or Anaconda first.")
        print("   Download from: https://docs.conda.io/en/latest/miniconda.html")
        return False
    
    # Try to create environment
    env_success, env_message = create_environment_simple()
    print(f"   {env_message}")
    
    if not env_success:
        print("\n❌ Environment creation failed.")
        print("   Try manual approach:")
        print("   conda create -n AyeSpy python=3.12")
        print("   conda activate AyeSpy") 
        print("   pip install -r requirements.txt")
        return False
    
    # Install packages
    pip_success, pip_message = install_pip_packages()
    if pip_success:
        print(f"   ✅ {pip_message}")
    else:
        print(f"   ⚠️  {pip_message}")
        
        # Try requirements.txt fallback
        req_success, req_message = use_requirements_txt()
        print(f"   {req_message}")
    
    # Test installation
    test_success, test_results = test_installation()
    for result in test_results:
        print(f"   {result}")
    
    if test_success:
        show_next_steps()
        return True
    else:
        print("\n⚠️  Setup completed with some issues.")
        print("   Basic functionality should work.")
        print("   You may need to install some packages manually.")
        show_next_steps()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
