#!/usr/bin/env python3
"""
Test script for ccapi-mcp Lambda handler.

This script validates the Lambda handler configuration and basic functionality.
"""

import json
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

def test_import():
    """Test that the Lambda handler syntax is valid."""
    try:
        # Read and compile the lambda function to check syntax
        with open('lambda_function.py', 'r') as f:
            code = f.read()
        
        compile(code, 'lambda_function.py', 'exec')
        print("✅ Lambda handler syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in Lambda handler: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating Lambda handler: {e}")
        return False

def test_mock_context():
    """Test MockClientContext class definition."""
    try:
        # Check that MockClientContext is properly defined in the code
        with open('lambda_function.py', 'r') as f:
            code = f.read()
        
        if 'class MockClientContext:' in code and 'bedrockAgentCoreToolName' in code:
            print("✅ MockClientContext is properly defined")
            return True
        else:
            print("❌ MockClientContext not found or incomplete")
            return False
    except Exception as e:
        print(f"❌ MockClientContext validation failed: {e}")
        return False

def test_configuration():
    """Test that the configuration is correct."""
    try:
        with open('lambda_function.py', 'r') as f:
            code = f.read()
        
        # Check for required configuration elements
        required_elements = [
            'awslabs.ccapi_mcp_server.server',
            'DEFAULT_TAGS',
            'SECURITY_SCANNING', 
            'FASTMCP_LOG_LEVEL',
            'AWS_ACCESS_KEY_ID',
            'BedrockAgentCoreGatewayTargetHandler'
        ]
        
        missing = []
        for element in required_elements:
            if element not in code:
                missing.append(element)
        
        if not missing:
            print("✅ All required configuration elements present")
            return True
        else:
            print(f"❌ Missing configuration elements: {missing}")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing ccapi-mcp Lambda handler...")
    print("=" * 50)
    
    tests = [
        ("Syntax Validation", test_import),
        ("MockClientContext Check", test_mock_context), 
        ("Configuration Check", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! ccapi-mcp handler is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())