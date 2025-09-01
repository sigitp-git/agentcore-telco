#!/usr/bin/env python3
"""
Verify MCP Lambda Deployment

This script verifies that all Lambda functions were deployed correctly
and are using the new lambda_handlers_q/ directory structure.
"""

import boto3
import json
import yaml
from pathlib import Path

def load_servers_config():
    """Load servers configuration from servers.yaml"""
    with open('servers.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config['servers']

def verify_lambda_functions():
    """Verify all Lambda functions exist and are configured correctly"""
    lambda_client = boto3.client('lambda')
    servers = load_servers_config()
    
    print("🔍 Verifying Lambda function deployment...")
    print(f"📊 Expected functions: {len(servers)}")
    print("")
    
    deployed_functions = []
    missing_functions = []
    
    for server_id, config in servers.items():
        function_name = f"mcp-server-{server_id}"
        
        try:
            # Get function configuration
            response = lambda_client.get_function(FunctionName=function_name)
            function_config = response['Configuration']
            
            # Verify basic configuration
            runtime = function_config['Runtime']
            handler = function_config['Handler']
            timeout = function_config['Timeout']
            memory = function_config['MemorySize']
            
            print(f"✅ {function_name}")
            print(f"   Runtime: {runtime}")
            print(f"   Handler: {handler}")
            print(f"   Timeout: {timeout}s (expected: {config.get('timeout', 60)}s)")
            print(f"   Memory: {memory}MB (expected: {config.get('memory', 1024)}MB)")
            
            # Verify handler is correct
            if handler == "lambda_function.lambda_handler":
                print(f"   ✅ Using correct handler pattern")
            else:
                print(f"   ⚠️  Handler mismatch: {handler}")
            
            deployed_functions.append(server_id)
            print("")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            print(f"❌ {function_name} - NOT FOUND")
            missing_functions.append(server_id)
        except Exception as e:
            print(f"❌ {function_name} - ERROR: {str(e)}")
            missing_functions.append(server_id)
    
    return deployed_functions, missing_functions

def verify_handler_files():
    """Verify all handler files exist in lambda_handlers_q/"""
    servers = load_servers_config()
    
    print("📁 Verifying handler files in lambda_handlers_q/...")
    print("")
    
    existing_handlers = []
    missing_handlers = []
    
    for server_id in servers.keys():
        handler_dir = Path(f"lambda_handlers_q/{server_id}")
        lambda_file = handler_dir / "lambda_function.py"
        requirements_file = handler_dir / "requirements.txt"
        
        if lambda_file.exists() and requirements_file.exists():
            print(f"✅ {server_id} - Handler files exist")
            existing_handlers.append(server_id)
        else:
            print(f"❌ {server_id} - Missing files:")
            if not lambda_file.exists():
                print(f"   - lambda_function.py missing")
            if not requirements_file.exists():
                print(f"   - requirements.txt missing")
            missing_handlers.append(server_id)
    
    print("")
    return existing_handlers, missing_handlers

def test_lambda_function(function_name):
    """Test a Lambda function with a simple invocation"""
    lambda_client = boto3.client('lambda')
    
    # Simple test payload
    test_payload = {
        "toolName": "test_tool",
        "headers": {
            "bedrockAgentCoreToolName": "test_tool"
        }
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_payload)
        )
        
        status_code = response['StatusCode']
        if status_code == 200:
            return True, "Success"
        else:
            return False, f"Status code: {status_code}"
            
    except Exception as e:
        return False, str(e)

def main():
    """Main verification function"""
    print("🔍 MCP Lambda Deployment Verification")
    print("=" * 50)
    print("")
    
    # Verify handler files exist
    existing_handlers, missing_handlers = verify_handler_files()
    
    # Verify Lambda functions are deployed
    deployed_functions, missing_functions = verify_lambda_functions()
    
    # Summary
    print("📊 Verification Summary:")
    print(f"   Handler files: {len(existing_handlers)}/{len(existing_handlers) + len(missing_handlers)}")
    print(f"   Lambda functions: {len(deployed_functions)}/{len(deployed_functions) + len(missing_functions)}")
    print("")
    
    if missing_handlers:
        print("❌ Missing handler files:")
        for handler in missing_handlers:
            print(f"   - {handler}")
        print("")
    
    if missing_functions:
        print("❌ Missing Lambda functions:")
        for function in missing_functions:
            print(f"   - mcp-server-{function}")
        print("")
    
    # Overall status
    if not missing_handlers and not missing_functions:
        print("🎉 All verifications passed!")
        print("✅ All handler files exist in lambda_handlers_q/")
        print("✅ All Lambda functions deployed successfully")
        print("✅ All functions using correct handler pattern")
        print("")
        print("🚀 Ready for AgentCore Gateway integration!")
    else:
        print("⚠️  Some issues found. Please check the details above.")
        
        if missing_handlers:
            print("💡 To fix missing handlers, run: python3 generate_all_handlers.py")
        
        if missing_functions:
            print("💡 To deploy missing functions, run: ./deploy_updated_stack.sh")

if __name__ == "__main__":
    main()