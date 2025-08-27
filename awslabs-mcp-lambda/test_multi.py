#!/usr/bin/env python3
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
        "core-mcp": "AWS Labs Core MCP Server",
        "aws-pricing": "AWS Pricing MCP Server",
        "aws-docs": "AWS Documentation MCP Server",
        "frontend-mcp": "AWS Labs Frontend MCP Server",
        "aws-location": "AWS Location MCP Server",
        "git-repo-research": "Git Repository Research MCP Server",
        "eks-mcp": "AWS EKS MCP Server",
        "aws-diagram": "AWS Diagram MCP Server",
        "prometheus": "Prometheus MCP Server",
        "cfn-mcp": "AWS CloudFormation MCP Server",
        "terraform-mcp": "Terraform MCP Server",
        "aws-knowledge": "AWS Knowledge MCP Server",
        "cloudwatch-mcp": "AWS CloudWatch MCP Server",
        "cloudwatch-appsignals": "AWS CloudWatch Application Signals MCP Server",
        "ccapi-mcp": "AWS Cloud Control API MCP Server",
        "github": "GitHub MCP Server",
        "git-repo": "Git Repository MCP Server (Legacy)",
        "filesystem": "Filesystem MCP Server",
    }
    
    passed = 0
    total = len(servers)
    
    for server_id, server_name in servers.items():
        print(f"\n🔍 Testing {server_name}...")
        if test_server(server_id, server_name):
            passed += 1
        print("-" * 40)
    
    print(f"\n📊 Test Results: {passed}/{total} servers passed")
    
    if passed == total:
        print("🎉 All servers passed! Ready to deploy.")
        return 0
    else:
        print("❌ Some servers failed. Please check the configurations.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
