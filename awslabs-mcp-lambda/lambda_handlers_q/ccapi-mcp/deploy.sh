#!/bin/bash

# AWS Cloud Control API MCP Server Lambda Deployment Script
# This script helps deploy and test the ccapi-mcp Lambda function

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "lambda_function.py" ]]; then
    print_error "lambda_function.py not found. Please run this script from the ccapi-mcp directory."
    exit 1
fi

print_status "Starting ccapi-mcp Lambda deployment process..."

# Step 1: Validate the implementation
print_status "Step 1: Validating implementation..."
if python3 test_handler.py; then
    print_status "✅ Implementation validation passed"
else
    print_error "❌ Implementation validation failed"
    exit 1
fi

# Step 2: Check dependencies
print_status "Step 2: Checking dependencies..."
if [[ -f "requirements.txt" ]]; then
    print_status "✅ requirements.txt found"
    cat requirements.txt
else
    print_error "❌ requirements.txt not found"
    exit 1
fi

# Step 3: Create deployment package (simulation)
print_status "Step 3: Preparing deployment package..."
print_status "Files to be included in deployment:"
ls -la *.py *.txt *.md 2>/dev/null || true

# Step 4: Validate AWS configuration
print_status "Step 4: Checking AWS configuration..."
if command -v aws &> /dev/null; then
    if aws sts get-caller-identity &> /dev/null; then
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        REGION=$(aws configure get region || echo "us-east-1")
        print_status "✅ AWS CLI configured - Account: ${ACCOUNT_ID}, Region: ${REGION}"
    else
        print_warning "⚠️  AWS CLI not authenticated. Please run 'aws configure' or set up credentials."
    fi
else
    print_warning "⚠️  AWS CLI not found. Install it for deployment capabilities."
fi

# Step 5: Show deployment instructions
print_status "Step 5: Deployment instructions..."
echo ""
echo "To deploy this Lambda function:"
echo ""
echo "1. Using AWS CLI:"
echo "   aws lambda create-function \\"
echo "     --function-name ccapi-mcp-function \\"
echo "     --runtime python3.9 \\"
echo "     --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \\"
echo "     --handler lambda_function.lambda_handler \\"
echo "     --zip-file fileb://deployment-package.zip"
echo ""
echo "2. Using Infrastructure as Code:"
echo "   - Add to the MCP Lambda stack in infrastructure/mcp_lambda_stack.py"
echo "   - Deploy using CDK: cdk deploy"
echo ""
echo "3. Using Terraform:"
echo "   - Add Lambda resource configuration"
echo "   - Apply with: terraform apply"
echo ""

# Step 6: Show testing instructions
print_status "Step 6: Testing instructions..."
echo ""
echo "After deployment, test the function:"
echo ""
echo "1. Test basic functionality:"
echo '   aws lambda invoke --function-name ccapi-mcp-function \\'
echo '     --payload '"'"'{"toolName": "list_resources", "parameters": {"resource_type": "AWS::S3::Bucket"}}'"'"' \\'
echo '     response.json'
echo ""
echo "2. Check logs:"
echo "   aws logs describe-log-groups --log-group-name-prefix '/aws/lambda/ccapi-mcp'"
echo ""

print_status "🎉 ccapi-mcp Lambda handler is ready for deployment!"
print_status "📚 See README.md for detailed documentation"