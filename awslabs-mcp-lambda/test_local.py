#!/usr/bin/env python3
"""
Local testing script for MCP Lambda wrapper

This script allows you to test the MCP wrapper locally before deploying.
"""

import json
import sys
import os

# Add lambda directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lambda'))

from handler import lambda_handler


def test_initialize():
    """Test MCP initialize request."""
    event = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    context = type('Context', (), {'aws_request_id': 'test-request-id'})()
    
    try:
        response = lambda_handler(event, context)
        print("✅ Initialize test passed")
        print(f"Response: {json.dumps(response, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Initialize test failed: {str(e)}")
        return False


def test_tools_list():
    """Test tools/list request."""
    event = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    context = type('Context', (), {'aws_request_id': 'test-request-id'})()
    
    try:
        response = lambda_handler(event, context)
        print("✅ Tools list test passed")
        print(f"Response: {json.dumps(response, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Tools list test failed: {str(e)}")
        return False


def test_api_gateway_format():
    """Test API Gateway request format."""
    event = {
        "body": json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "initialize",
            "params": {}
        }),
        "headers": {
            "Content-Type": "application/json"
        }
    }
    
    context = type('Context', (), {'aws_request_id': 'test-request-id'})()
    
    try:
        response = lambda_handler(event, context)
        print("✅ API Gateway format test passed")
        print(f"Response: {json.dumps(response, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ API Gateway format test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing MCP Lambda wrapper locally...")
    print("=" * 50)
    
    tests = [
        test_initialize,
        test_tools_list,
        test_api_gateway_format
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n🔍 Running {test.__name__}...")
        if test():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready to deploy.")
        return 0
    else:
        print("❌ Some tests failed. Please check the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())