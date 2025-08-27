#!/bin/bash

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
echo "  - AWS Labs Core MCP Server: mcp-server-core-mcp"
echo "  - AWS Pricing MCP Server: mcp-server-aws-pricing"
echo "  - AWS Documentation MCP Server: mcp-server-aws-docs"
echo "  - AWS Labs Frontend MCP Server: mcp-server-frontend-mcp"
echo "  - AWS Location MCP Server: mcp-server-aws-location"
echo "  - Git Repository Research MCP Server: mcp-server-git-repo-research"
echo "  - AWS EKS MCP Server: mcp-server-eks-mcp"
echo "  - AWS Diagram MCP Server: mcp-server-aws-diagram"
echo "  - Prometheus MCP Server: mcp-server-prometheus"
echo "  - AWS CloudFormation MCP Server: mcp-server-cfn-mcp"
echo "  - Terraform MCP Server: mcp-server-terraform-mcp"
echo "  - AWS Knowledge MCP Server: mcp-server-aws-knowledge"
echo "  - AWS CloudWatch MCP Server: mcp-server-cloudwatch-mcp"
echo "  - AWS CloudWatch Application Signals MCP Server: mcp-server-cloudwatch-appsignals"
echo "  - AWS Cloud Control API MCP Server: mcp-server-ccapi-mcp"
echo "  - GitHub MCP Server: mcp-server-github"
echo "  - Git Repository MCP Server (Legacy): mcp-server-git-repo"
echo "  - Filesystem MCP Server: mcp-server-filesystem"

echo ""
echo "📋 Next steps:"
echo "1. Copy the Lambda ARNs from the output above"
echo "2. Configure your AgentCore Gateway to use these Lambda functions"
echo "3. Each MCP server now has its own dedicated Lambda function"
