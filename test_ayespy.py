#!/usr/bin/env python3
"""
Quick test script for AyeSpy after successful installation.
"""

import sys
import os
import webbrowser
import time
import subprocess
from threading import Thread

def test_imports():
    """Test that all core packages can be imported."""
    print("🧪 Testing package imports...")
    
    tests = [
        ('flask', 'Flask web framework'),
        ('pandas', 'Data processing'),
        ('rich', 'Terminal UI'),
        ('requests', 'HTTP client'),
        ('sqlalchemy', 'Database ORM'),
        ('psycopg2', 'PostgreSQL connector')
    ]
    
    success_count = 0
    for package, description in tests:
        try:
            __import__(package)
            print(f"   ✅ {package:<12} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"   ❌ {package:<12} - {description} (Error: {e})")
    
    print(f"\n📊 Import test: {success_count}/{len(tests)} packages working")
    return success_count >= 4

def test_ui_import():
    """Test that the UI can be imported."""
    print("\n🌐 Testing UI import...")
    try:
        from ui import app
        print("   ✅ Flask app imports successfully")
        return True
    except Exception as e:
        print(f"   ❌ UI import failed: {e}")
        return False

def test_data_files():
    """Test that data files exist."""
    print("\n📁 Testing data files...")
    
    files = [
        'congressional_hearings_test2.csv',
        'data/legislators-current.csv',
        'data/committee_data.csv'
    ]
    
    success_count = 0
    for file_path in files:
        if os.path.exists(file_path):
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                print(f"   ✅ {file_path:<35} ({len(df)} records)")
                success_count += 1
            except Exception as e:
                print(f"   ⚠️  {file_path:<35} (exists but has issues: {e})")
        else:
            print(f"   ❌ {file_path:<35} (missing)")
    
    print(f"\n📊 Data files: {success_count}/{len(files)} files accessible")
    return success_count >= 1

def start_ui_and_test():
    """Start the UI and test it."""
    print("\n🚀 Starting AyeSpy web interface...")
    
    try:
        # Start UI in background
        print("   Starting Flask server...")
        process = subprocess.Popen([sys.executable, 'ui.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test if server is responding
        try:
            import requests
            response = requests.get('http://localhost:5000', timeout=5)
            if response.status_code == 200:
                print("   ✅ Web server is running!")
                print("   🌐 Open your browser to: http://localhost:5000")
                
                # Try to open browser
                try:
                    webbrowser.open('http://localhost:5000')
                    print("   🌐 Browser opened automatically")
                except:
                    print("   🌐 Please open http://localhost:5000 manually")
                
                return True, process
            else:
                print(f"   ❌ Server responded with status {response.status_code}")
                return False, process
                
        except Exception as e:
            print(f"   ❌ Server test failed: {e}")
            return False, process
            
    except Exception as e:
        print(f"   ❌ Failed to start UI: {e}")
        return False, None

def main():
    """Main test function."""
    print("🏛️  AyeSpy System Test")
    print("=" * 50)
    
    # Test 1: Package imports
    imports_ok = test_imports()
    
    # Test 2: UI import
    ui_import_ok = test_ui_import()
    
    # Test 3: Data files
    data_ok = test_data_files()
    
    # Test 4: Start UI
    ui_running = False
    process = None
    
    if imports_ok and ui_import_ok:
        ui_running, process = start_ui_and_test()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    print(f"✅ Package imports:    {'PASS' if imports_ok else 'FAIL'}")
    print(f"✅ UI import:          {'PASS' if ui_import_ok else 'FAIL'}")
    print(f"✅ Data files:         {'PASS' if data_ok else 'FAIL'}")
    print(f"✅ Web server:         {'PASS' if ui_running else 'FAIL'}")
    
    if ui_running:
        print("\n🎉 AYSPY IS WORKING!")
        print("\n📋 What you can do now:")
        print("• 🌐 Use the web interface at http://localhost:5000")
        print("• 🔍 Try searching for politicians like 'Biden' or 'Pelosi'")
        print("• 📝 Enter issues like 'healthcare' or 'defense'")
        print("• ⏰ Test different time range filters")
        print("\n💻 Terminal interface:")
        print("• python main.py")
        print("\n🛑 To stop the web server:")
        print("• Press Ctrl+C in the terminal")
        
        # Keep running until user stops
        try:
            print("\n⏳ Web server running... Press Ctrl+C to stop")
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping web server...")
            if process:
                process.terminate()
            print("✅ Web server stopped")
        
        return True
    else:
        print("\n⚠️  AYSPY HAS ISSUES")
        print("\n🔧 Troubleshooting:")
        if not imports_ok:
            print("• Install missing packages: pip install flask pandas rich requests")
        if not ui_import_ok:
            print("• Check ui.py file for syntax errors")
        if not data_ok:
            print("• Verify data files are in the correct location")
        print("\n📖 For detailed help, see START_HERE.md")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
