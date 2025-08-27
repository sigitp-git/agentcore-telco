#!/usr/bin/env python3
"""
Test script to verify MCP Lambda setup
"""

import yaml
import json
import os
from pathlib import Path

def test_configuration():
    """Test that all configurations are valid"""
    print("🧪 Testing MCP Lambda configuration...")
    
    # Test servers.yaml
    try:
        with open('servers.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        servers = config.get('servers', {})
        print(f"✅ Found {len(servers)} MCP servers in configuration")
        
        for server_id, server_config in servers.items():
            name = server_config.get('name', 'Unknown')
            command = server_config.get('command', 'Unknown')
            print(f"  - {server_id}: {name} ({command})")
            
            # Validate required fields
            if not server_config.get('command'):
                print(f"    ❌ Missing 'command' field")
                return False
            if not server_config.get('args'):
                print(f"    ❌ Missing 'args' field")
                return False
                
        print("✅ All server configurations are valid")
        
    except Exception as e:
        print(f"❌ Error reading servers.yaml: {e}")
        return False
    
    # Test infrastructure files
    required_files = [
        'app.py',
        'infrastructure/__init__.py',
        'infrastructure/mcp_lambda_stack.py',
        'requirements.txt',
        'cdk.json'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing required file: {file_path}")
            return False
        print(f"✅ Found {file_path}")
    
    # Test lambda_handlers directory
    if not os.path.exists('lambda_handlers'):
        print("❌ Missing lambda_handlers directory")
        return False
    print("✅ Found lambda_handlers directory")
    
    return True

def generate_agentcore_config():
    """Generate sample AgentCore Gateway configuration"""
    print("\\n📋 Generating sample AgentCore Gateway configuration...")
    
    with open('servers.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    servers = config.get('servers', {})
    
    agentcore_config = {
        "mcpServers": {}
    }
    
    for server_id, server_config in servers.items():
        agentcore_config["mcpServers"][server_id] = {
            "type": "lambda",
            "arn": f"arn:aws:lambda:REGION:ACCOUNT:function:mcp-server-{server_id}",
            "description": server_config.get('description', server_config.get('name', ''))
        }
    
    # Save to file
    with open('agentcore-gateway-config.json', 'w') as f:
        json.dump(agentcore_config, f, indent=2)
    
    print("✅ Generated agentcore-gateway-config.json")
    print("\\n💡 Sample configuration for AgentCore Gateway:")
    print(json.dumps(agentcore_config, indent=2)[:500] + "...")

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 MCP Lambda Setup Test")
    print("=" * 60)
    
    if test_configuration():
        print("\\n🎉 All tests passed! Ready to deploy.")
        generate_agentcore_config()
        
        print("\\n📋 Next steps:")
        print("1. Run './deploy.sh' to deploy Lambda functions")
        print("2. Update REGION and ACCOUNT in agentcore-gateway-config.json")
        print("3. Configure your AgentCore Gateway with the Lambda ARNs")
        
        return 0
    else:
        print("\\n❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())