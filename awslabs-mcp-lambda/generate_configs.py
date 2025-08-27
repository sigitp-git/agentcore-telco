#!/usr/bin/env python3
"""
Generate individual Lambda configurations from servers.yaml

This script creates separate Lambda code directories for each MCP server,
enabling 1:1 mapping of servers to Lambda functions.
"""

import os
import sys
import yaml
import json
import shutil
from pathlib import Path


def load_server_configs():
    """Load server configurations from servers.yaml"""
    with open('servers.yaml', 'r') as f:
        return yaml.safe_load(f)


def create_lambda_directory(server_id: str, config: dict):
    """Create a Lambda directory for a specific server."""
    lambda_dir = f"lambda-{server_id}"
    
    # Create directory
    os.makedirs(lambda_dir, exist_ok=True)
    
    # Copy base files
    base_files = [
        "lambda/handler.py",
        "lambda/mcp_wrapper.py", 
        "lambda/requirements.txt"
    ]
    
    for file_path in base_files:
        if os.path.exists(file_path):
            shutil.copy2(file_path, lambda_dir)
    
    # Create server-specific config.py
    config_content = f'''"""
MCP Server Configuration for {server_id}

Auto-generated configuration for {config['name']}.
"""

# Configuration for the MCP server to wrap
MCP_SERVER_CONFIG = {json.dumps({
    "command": config["command"],
    "args": config["args"],
    "env": config.get("env", {})
}, indent=4)}
'''
    
    with open(f"{lambda_dir}/config.py", "w") as f:
        f.write(config_content)
    
    print(f"✅ Created Lambda directory: {lambda_dir}")
    return lambda_dir


def generate_deployment_script(servers: dict):
    """Generate a deployment script for all servers."""
    script_content = '''#!/bin/bash

# Deploy script for Multi-MCP Lambda functions

set -e

echo "🚀 Deploying Multi-MCP Lambda functions..."

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ AWS CDK is not installed. Please install it first:"
    echo "npm install -g aws-cdk"
    exit 1
fi

# Check if Python dependencies are installed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Generate Lambda configurations
echo "🔧 Generating Lambda configurations..."
python generate_configs.py

# Bootstrap CDK if needed
echo "🔧 Checking CDK bootstrap..."
cdk bootstrap

# Deploy the stack
echo "🚀 Deploying stack..."
cdk deploy --require-approval never

echo "✅ Deployment complete!"
echo ""
echo "📋 Lambda Functions Created:"
'''
    
    for server_id, config in servers.items():
        script_content += f'echo "  - {config["name"]}: mcp-server-{server_id}"\n'
    
    script_content += '''
echo ""
echo "📋 Next steps:"
echo "1. Copy the Lambda ARNs from the output above"
echo "2. Configure your AgentCore Gateway to use these Lambda functions"
echo "3. Each MCP server now has its own dedicated Lambda function"
'''
    
    with open("deploy_multi.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("deploy_multi.sh", 0o755)
    print("✅ Created deployment script: deploy_multi.sh")


def generate_test_script(servers: dict):
    """Generate a test script for all servers."""
    script_content = '''#!/usr/bin/env python3
"""
Test all MCP Lambda functions locally
"""

import json
import sys
import os
from pathlib import Path

def test_server(server_id: str, server_name: str):
    """Test a specific MCP server."""
    lambda_dir = f"lambda-{server_id}"
    
    if not os.path.exists(lambda_dir):
        print(f"❌ Lambda directory not found: {lambda_dir}")
        return False
    
    # Add lambda directory to path
    sys.path.insert(0, lambda_dir)
    
    try:
        from handler import lambda_handler
        
        # Test initialize request
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
        
        context = type('Context', (), {'aws_request_id': f'test-{server_id}'})()
        
        response = lambda_handler(event, context)
        print(f"✅ {server_name} test passed")
        return True
        
    except Exception as e:
        print(f"❌ {server_name} test failed: {str(e)}")
        return False
    finally:
        # Remove from path
        if lambda_dir in sys.path:
            sys.path.remove(lambda_dir)

def main():
    """Test all servers."""
    print("🧪 Testing all MCP Lambda functions locally...")
    print("=" * 60)
    
    servers = {
'''
    
    for server_id, config in servers.items():
        script_content += f'        "{server_id}": "{config["name"]}",\n'
    
    script_content += '''    }
    
    passed = 0
    total = len(servers)
    
    for server_id, server_name in servers.items():
        print(f"\\n🔍 Testing {server_name}...")
        if test_server(server_id, server_name):
            passed += 1
        print("-" * 40)
    
    print(f"\\n📊 Test Results: {passed}/{total} servers passed")
    
    if passed == total:
        print("🎉 All servers passed! Ready to deploy.")
        return 0
    else:
        print("❌ Some servers failed. Please check the configurations.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open("test_multi.py", "w") as f:
        f.write(script_content)
    
    os.chmod("test_multi.py", 0o755)
    print("✅ Created test script: test_multi.py")


def main():
    """Generate all Lambda configurations."""
    print("🔧 Generating Lambda configurations for MCP servers...")
    
    # Load server configurations
    config = load_server_configs()
    servers = config.get('servers', {})
    
    if not servers:
        print("❌ No servers found in servers.yaml")
        return 1
    
    print(f"📋 Found {len(servers)} MCP servers to configure:")
    for server_id, server_config in servers.items():
        print(f"  - {server_id}: {server_config['name']}")
    
    print()
    
    # Create Lambda directories for each server
    for server_id, server_config in servers.items():
        create_lambda_directory(server_id, server_config)
    
    # Generate deployment and test scripts
    generate_deployment_script(servers)
    generate_test_script(servers)
    
    print()
    print("✅ All configurations generated successfully!")
    print()
    print("📋 Next steps:")
    print("1. Run: ./test_multi.py (test locally)")
    print("2. Run: ./deploy_multi.sh (deploy to AWS)")
    print("3. Use the Lambda ARNs in your AgentCore Gateway configuration")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())