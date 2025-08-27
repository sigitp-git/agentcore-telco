#!/usr/bin/env python3
"""
Test deployed Lambda functions to verify they work correctly
"""

import json
import boto3
import time
from typing import Dict, Any, List


def test_lambda_function(function_name: str, test_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single Lambda function with a given payload"""
    
    lambda_client = boto3.client('lambda')
    
    try:
        print(f"🧪 Testing {function_name}...")
        
        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_payload)
        )
        
        # Parse the response
        status_code = response['StatusCode']
        payload = json.loads(response['Payload'].read())
        
        print(f"   Status Code: {status_code}")
        
        if status_code == 200:
            print(f"   ✅ Success")
            if 'errorMessage' in payload:
                print(f"   ⚠️  Error in payload: {payload['errorMessage']}")
                return {'success': False, 'error': payload['errorMessage'], 'payload': payload}
            else:
                print(f"   📄 Response: {json.dumps(payload, indent=2)[:200]}...")
                return {'success': True, 'payload': payload}
        else:
            print(f"   ❌ Failed with status {status_code}")
            return {'success': False, 'error': f"HTTP {status_code}", 'payload': payload}
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return {'success': False, 'error': str(e)}


def test_mcp_initialize_request() -> Dict[str, Any]:
    """Create a standard MCP initialize request"""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }


def main():
    """Test all deployed Lambda functions"""
    
    print("🚀 Testing MCP Lambda Functions")
    print("=" * 50)
    
    # List of Lambda functions to test
    lambda_functions = [
        "mcp-server-core-mcp",
        "mcp-server-aws-pricing", 
        "mcp-server-aws-docs",
        "mcp-server-frontend-mcp",
        "mcp-server-aws-location"
    ]
    
    # Test payload - MCP initialize request
    test_payload = test_mcp_initialize_request()
    
    results = {}
    
    for function_name in lambda_functions:
        result = test_lambda_function(function_name, test_payload)
        results[function_name] = result
        print()  # Add spacing between tests
        
        # Add a small delay to avoid throttling
        time.sleep(1)
    
    # Summary
    print("📊 Test Summary")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for function_name, result in results.items():
        if result['success']:
            print(f"✅ {function_name}")
            successful += 1
        else:
            print(f"❌ {function_name}: {result['error']}")
            failed += 1
    
    print(f"\n📈 Results: {successful} successful, {failed} failed")
    
    if failed > 0:
        print("\n🔧 Common Issues:")
        print("- Lambda functions may need proper MCP server implementations")
        print("- Current subprocess approach won't work in Lambda environment")
        print("- Need to bundle MCP servers as native Python packages")
        
    return results


if __name__ == "__main__":
    main()