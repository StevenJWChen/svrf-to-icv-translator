#!/usr/bin/env python3
"""
Comprehensive Test Suite for SVRF to ICV Translator
Tests all functionality and validates the project completion
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_parser():
    """Test SVRF parser functionality"""
    print("🧪 Testing SVRF Parser...")
    
    success, output, error = run_command("python simple_svrf_parser.py example_drc_rules.svrf")
    if success:
        print("  ✅ Basic parsing - PASSED")
    else:
        print(f"  ❌ Basic parsing - FAILED: {error}")
        return False
    
    # Test with layers and rules display
    success, output, error = run_command("python simple_svrf_parser.py example_drc_rules.svrf --layers --rules")
    if success and "Layers:" in output:
        print("  ✅ Analysis mode - PASSED")
    else:
        print("  ❌ Analysis mode - FAILED")
        return False
    
    return True

def test_translator():
    """Test SVRF to ICV translator"""
    print("🧪 Testing SVRF to ICV Translator...")
    
    # Test basic translation
    success, output, error = run_command("python svrf_to_icv_translator.py example_drc_rules.svrf")
    if success and "completed successfully" in output:
        print("  ✅ Basic translation - PASSED")
    else:
        print(f"  ❌ Basic translation - FAILED: {error}")
        return False
    
    # Test with summary
    success, output, error = run_command("python svrf_to_icv_translator.py example_drc_rules.svrf --summary")
    if success:
        print("  ✅ Summary mode - PASSED")
    else:
        print("  ❌ Summary mode - FAILED")
        return False
    
    return True

def test_enhanced_translator():
    """Test enhanced translator"""
    print("🧪 Testing Enhanced Translator...")
    
    success, output, error = run_command("python final_enhanced_translator.py test_comprehensive.svrf")
    if success and "100.0% coverage achieved" in output:
        print("  ✅ Enhanced translator - PASSED")
        print("  ✅ 100% coverage achieved - PASSED")
    else:
        print(f"  ❌ Enhanced translator - FAILED: {error}")
        return False
    
    return True

def test_complex_files():
    """Test with complex rule files"""
    print("🧪 Testing Complex Rule Files...")
    
    # Test complex rules
    if os.path.exists("complex_drc_rules.svrf"):
        success, output, error = run_command("python final_enhanced_translator.py complex_drc_rules.svrf")
        if success:
            print("  ✅ Complex rules translation - PASSED")
        else:
            print("  ❌ Complex rules translation - FAILED")
            return False
    else:
        print("  ⚠️  Complex rules file not found - SKIPPED")
    
    return True

def test_file_outputs():
    """Test output file generation"""
    print("🧪 Testing Output File Generation...")
    
    # Check if ICV files are generated
    expected_files = ["example_drc_rules.icv", "test_comprehensive.icv"]
    
    for file in expected_files:
        if os.path.exists(file):
            print(f"  ✅ {file} generated - PASSED")
            
            # Check file content
            with open(file, 'r') as f:
                content = f.read()
                if "LAYER" in content and "rule" in content:
                    print(f"  ✅ {file} content valid - PASSED")
                else:
                    print(f"  ❌ {file} content invalid - FAILED")
                    return False
        else:
            print(f"  ❌ {file} not generated - FAILED")
            return False
    
    return True

def test_demos():
    """Test demo scripts"""
    print("🧪 Testing Demo Scripts...")
    
    # Test parser demo
    success, output, error = run_command("python demo_parser.py")
    if success and "SVRF DRC Parser Demo" in output:
        print("  ✅ Parser demo - PASSED")
    else:
        print("  ❌ Parser demo - FAILED")
        return False
    
    # Test translator demo
    success, output, error = run_command("python demo_translator.py")
    if success and "SVRF to ICV Translator Demo" in output:
        print("  ✅ Translator demo - PASSED")
    else:
        print("  ❌ Translator demo - FAILED")
        return False
    
    return True

def validate_project_structure():
    """Validate project structure and files"""
    print("🧪 Validating Project Structure...")
    
    required_files = [
        "README.md",
        "requirements.txt", 
        "LICENSE",
        "simple_svrf_parser.py",
        "svrf_to_icv_translator.py", 
        "final_enhanced_translator.py",
        "demo_parser.py",
        "demo_translator.py",
        "example_drc_rules.svrf"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file} exists - PASSED")
        else:
            print(f"  ❌ {file} missing - FAILED")
            return False
    
    return True

def test_documentation():
    """Test documentation completeness"""
    print("🧪 Testing Documentation...")
    
    with open("README.md", 'r') as f:
        readme_content = f.read()
        
    required_sections = [
        "Installation",
        "Quick Start", 
        "Usage Examples",
        "Features"
    ]
    
    for section in required_sections:
        if section in readme_content:
            print(f"  ✅ README contains {section} - PASSED")
        else:
            print(f"  ❌ README missing {section} - FAILED")
            return False
    
    return True

def test_rule_coverage():
    """Test rule type coverage"""
    print("🧪 Testing Rule Type Coverage...")
    
    # Test that all major rule types are supported
    success, output, error = run_command("python final_enhanced_translator.py test_comprehensive.svrf")
    
    expected_rule_types = [
        "width check",
        "spacing check", 
        "area check",
        "enclosure check",
        "density check",
        "antenna check"
    ]
    
    for rule_type in expected_rule_types:
        if rule_type in output:
            print(f"  ✅ {rule_type} supported - PASSED")
        else:
            print(f"  ❌ {rule_type} not found - FAILED")
            return False
    
    return True

def main():
    """Main test runner"""
    print("=" * 60)
    print("🚀 SVRF to ICV Translator - Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Project Structure", validate_project_structure),
        ("Documentation", test_documentation), 
        ("SVRF Parser", test_parser),
        ("Basic Translator", test_translator),
        ("Enhanced Translator", test_enhanced_translator),
        ("Complex Files", test_complex_files),
        ("Output Files", test_file_outputs),
        ("Demo Scripts", test_demos),
        ("Rule Coverage", test_rule_coverage)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"  🎯 {test_name} - OVERALL PASSED")
            else:
                print(f"  💥 {test_name} - OVERALL FAILED")
        except Exception as e:
            print(f"  💥 {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("✅ Project is complete and ready for production!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed.")
        print("❌ Project needs attention before completion.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)