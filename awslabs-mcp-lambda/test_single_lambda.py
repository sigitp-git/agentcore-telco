#!/usr/bin/env python3
"""
Test a single Lambda function to see what happens with the current implementation
"""

import json
import boto3
import sys


def test_single_lambda():
    """Test one Lambda function to see the actual error"""
    
    # Use the region from our deployment
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    function_name = sys.argv[1] if len(sys.argv) > 1 else "mcp-server-core-mcp"
    
    # MCP initialize request
    test_payload = {
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
    
    print(f"🧪 Testing {function_name}")
    print(f"📤 Payload: {json.dumps(test_payload, indent=2)}")
    print()
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_payload)
        )
        
        status_code = response['StatusCode']
        payload = json.loads(response['Payload'].read())
        
        print(f"📊 Status Code: {status_code}")
        print(f"📥 Response: {json.dumps(payload, indent=2)}")
        
        if 'errorMessage' in payload:
            print(f"\n❌ Error Details:")
            print(f"   Message: {payload['errorMessage']}")
            if 'errorType' in payload:
                print(f"   Type: {payload['errorType']}")
            if 'stackTrace' in payload:
                print(f"   Stack Trace: {payload['stackTrace'][:3]}")  # First 3 lines
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")


if __name__ == "__main__":
    test_single_lambda()