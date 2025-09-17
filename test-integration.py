#!/usr/bin/env python3
"""
Test script for SD-Tailnokio notebook integration
This script helps verify that all components are working correctly.
"""

import sys
import os

def test_imports():
    """Test that all core modules can be imported."""
    print("🔍 Testing core module imports...")
    
    try:
        from core.cloud_detection.cloud_detector import CloudDetector
        print("✅ CloudDetector imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CloudDetector: {e}")
        return False
    
    try:
        from core.environment_management.shell_runner import ShellRunner
        print("✅ ShellRunner imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ShellRunner: {e}")
        return False
    
    try:
        from core.app_database import AppDatabase
        print("✅ AppDatabase imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AppDatabase: {e}")
        return False
    
    try:
        from core.app_manager import AppManager
        print("✅ AppManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AppManager: {e}")
        return False
    
    try:
        from core.tunneling.cloudflare_manager import CloudflareManager
        print("✅ CloudflareManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CloudflareManager: {e}")
        return False
    
    return True

def test_functionality():
    """Test basic functionality of core components."""
    print("\n🔍 Testing core functionality...")
    
    try:
        # Test CloudDetector
        from core.cloud_detection.cloud_detector import CloudDetector
        detector = CloudDetector()
        platform = detector.detect_platform()
        print(f"✅ CloudDetector working - Detected platform: {platform}")
    except Exception as e:
        print(f"❌ CloudDetector test failed: {e}")
        return False
    
    try:
        # Test ShellRunner
        from core.environment_management.shell_runner import ShellRunner
        runner = ShellRunner()
        result = runner.run_command("echo 'test'", capture_output=True)
        if result.get('success') and 'test' in result.get('output', ''):
            print("✅ ShellRunner working - Command execution successful")
        else:
            print("❌ ShellRunner test failed - Command execution issue")
            return False
    except Exception as e:
        print(f"❌ ShellRunner test failed: {e}")
        return False
    
    try:
        # Test AppDatabase
        from core.app_database import AppDatabase
        db = AppDatabase()
        apps_loaded = db.load_applications()
        print(f"✅ AppDatabase working - Loaded {apps_loaded} applications")
    except Exception as e:
        print(f"❌ AppDatabase test failed: {e}")
        return False
    
    return True

def test_dependencies():
    """Test that required dependencies are available."""
    print("\n🔍 Testing external dependencies...")
    
    required_packages = ['flask', 'requests', 'qrcode', 'pillow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install " + " ".join(missing_packages))
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Testing SD-Tailnokio Integration")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Functionality
    if test_functionality():
        tests_passed += 1
    
    # Test 3: Dependencies
    if test_dependencies():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! SD-Tailnokio is ready to use.")
        print("\nTo start the notebook interface:")
        print("  %run notebook-integration.py")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)