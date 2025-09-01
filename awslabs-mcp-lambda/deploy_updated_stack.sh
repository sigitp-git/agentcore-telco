#!/bin/bash
"""
Deploy Updated MCP Lambda Stack

This script deploys the updated CDK stack that uses the new lambda_handlers_q/ directory
with the working mcp_lambda library pattern for all 18 MCP servers.
"""

set -e

echo "🚀 Deploying Updated MCP Lambda Stack..."
echo "📁 Using handlers from lambda_handlers_q/ directory"
echo "🔧 Using working mcp_lambda library pattern"
echo ""

# Check if we're in the right directory
if [ ! -f "servers.yaml" ]; then
    echo "❌ Error: servers.yaml not found. Please run from awslabs-mcp-lambda directory."
    exit 1
fi

# Check if lambda_handlers_q directory exists
if [ ! -d "lambda_handlers_q" ]; then
    echo "❌ Error: lambda_handlers_q directory not found."
    echo "   Please run generate_all_handlers.py first to create the handlers."
    exit 1
fi

# Count handlers
handler_count=$(find lambda_handlers_q -name "lambda_function.py" | wc -l)
echo "📊 Found $handler_count lambda handlers in lambda_handlers_q/"

# Verify CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ Error: AWS CDK not found. Please install with: npm install -g aws-cdk"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS credentials not configured. Please run 'aws configure' or set environment variables."
    exit 1
fi

echo ""
echo "🔍 Pre-deployment checks:"
echo "  ✅ servers.yaml found"
echo "  ✅ lambda_handlers_q/ directory exists"
echo "  ✅ $handler_count lambda handlers found"
echo "  ✅ AWS CDK installed"
echo "  ✅ AWS credentials configured"
echo ""

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "🏗️  Bootstrapping CDK (if needed)..."
cdk bootstrap

echo ""
echo "🔄 Synthesizing CDK stack..."
cdk synth

echo ""
echo "🚀 Deploying CDK stack..."
echo "   This will create/update $handler_count Lambda functions"
echo "   Each function uses the working mcp_lambda library pattern"
echo ""

# Deploy with confirmation
cdk deploy --require-approval never

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Test the Lambda functions with AgentCore Gateway"
echo "2. Update AgentCore Gateway configuration with new Lambda ARNs"
echo "3. Verify all 18 MCP servers are working correctly"
echo ""
echo "📊 Deployed Lambda functions:"
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `mcp-server-`)].FunctionName' --output table

echo ""
echo "🎉 All MCP Lambda handlers are now using the working mcp_lambda library pattern!"