# AWS Labs MCP Lambda - Multi-Server Architecture

A Lambda wrapper system for running multiple stdio-based Model Context Protocol (MCP) servers on AWS Lambda with **1:1 mapping** - one Lambda function per MCP server. Designed for integration with Amazon Bedrock AgentCore Gateway.

## 🎯 Architecture Overview

This project creates **dedicated Lambda functions** for each MCP server, providing:
- **Isolation**: Each MCP server runs in its own Lambda function
- **Scaling**: Independent scaling per MCP server based on usage
- **Management**: Easy to manage, update, and monitor individual servers
- **Cost Optimization**: Pay only for what each server uses

## 🚀 Supported MCP Servers (18 Total)

Configure any stdio-based MCP server in `servers.yaml`. Currently configured:

### **AWS Labs MCP Servers (15)**
- **Core MCP**: `awslabs.core-mcp-server` - Core AWS functionality
- **AWS Documentation**: `awslabs.aws-documentation-mcp-server` - AWS docs search
- **AWS Pricing**: `awslabs.aws-pricing-mcp-server` - AWS pricing info
- **Frontend MCP**: `awslabs.frontend-mcp-server` - React/frontend tools
- **AWS Location**: `awslabs.aws-location-mcp-server` - Location services
- **Git Repo Research**: `awslabs.git-repo-research-mcp-server` - Advanced git analysis
- **EKS MCP**: `awslabs.eks-mcp-server` - Kubernetes management
- **AWS Diagram**: `awslabs.aws-diagram-mcp-server` - Architecture diagrams
- **Prometheus**: `awslabs.prometheus-mcp-server` - Metrics monitoring
- **CloudFormation**: `awslabs.cfn-mcp-server` - CFN management
- **Terraform**: `awslabs.terraform-mcp-server` - Infrastructure as code
- **AWS Knowledge**: `mcp-proxy` - AWS knowledge base
- **CloudWatch**: `awslabs.cloudwatch-mcp-server` - Logs and metrics
- **CloudWatch AppSignals**: `awslabs.cloudwatch-appsignals-mcp-server` - Application monitoring
- **Cloud Control API**: `awslabs.ccapi-mcp-server` - AWS resource management

### **Third-party MCP Servers (3)**
- **GitHub**: `ghcr.io/github/github-mcp-server` - GitHub operations
- **Git Repository (Legacy)**: `mcp-server-git` - Basic git operations
- **Filesystem**: `mcp-server-filesystem` - File system access

## 📁 Project Structure

```
awslabs-mcp-lambda/
├── README.md                    # This file
├── servers.yaml                 # MCP server configurations
├── requirements.txt             # CDK dependencies
├── app.py                      # Multi-Lambda CDK application
├── generate_configs.py         # Generate Lambda configs per server
├── lambda/                     # Base Lambda code (template)
│   ├── handler.py             # Lambda handler
│   ├── mcp_wrapper.py         # MCP server wrapper
│   └── requirements.txt       # Lambda runtime dependencies
├── lambda-{server-id}/         # Generated per-server Lambda code
├── infrastructure/
│   └── multi_lambda_stack.py  # Multi-Lambda CDK stack
└── tests/
```

## ⚡ Quick Start

### 1. **Configure Your MCP Servers**
The project comes pre-configured with 18 MCP servers in `servers.yaml`. You can customize which servers to deploy:

```yaml
servers:
  core-mcp:
    name: "AWS Labs Core MCP Server"
    command: "uvx"
    args: ["awslabs.core-mcp-server@latest"]
    env:
      FASTMCP_LOG_LEVEL: "ERROR"
    timeout: 60
    memory: 1024

  eks-mcp:
    name: "AWS EKS MCP Server"
    command: "uvx"
    args: ["awslabs.eks-mcp-server@latest", "--allow-write", "--allow-sensitive-data-access"]
    env:
      FASTMCP_LOG_LEVEL: "ERROR"
    timeout: 120
    memory: 2048

  github:
    name: "GitHub MCP Server"
    command: "docker"
    args: ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"]
    env:
      FASTMCP_LOG_LEVEL: "ERROR"
    timeout: 90
    memory: 1536
```

### 2. **Generate Lambda Configurations**
```bash
python generate_configs.py
```
This creates `lambda-{server-id}/` directories with server-specific configurations.

### 3. **Test Locally**
```bash
./test_multi.py
```

### 4. **Deploy to AWS**
```bash
./deploy_multi.sh
```

### 5. **Get Lambda ARNs for AgentCore Gateway**
After deployment, you'll get individual Lambda ARNs for all 18 servers:
```
McpCoremcpLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-core-mcp
McpAwspricingLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-pricing
McpAwsdocsLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-docs
McpEksmcpLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-eks-mcp
McpGithubLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-github
# ... and 13 more servers
```

## 🔧 AgentCore Gateway Configuration

Configure each Lambda ARN as a separate MCP server in your AgentCore Gateway:

```json
{
  "mcpServers": {
    "core-mcp": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-core-mcp",
      "description": "Core AWS functionality and prompt understanding"
    },
    "aws-docs": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-docs",
      "description": "AWS documentation search and retrieval"
    },
    "eks-mcp": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-eks-mcp",
      "description": "Amazon EKS cluster management"
    },
    "github": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-github",
      "description": "GitHub repository and issue management"
    }
    // ... configure all 18 servers as needed
  }
}
```

## 🎛️ Server Configuration Options

Each server in `servers.yaml` supports:

```yaml
server-id:
  name: "Human readable name"
  description: "Server description"
  command: "uvx"                    # Command to run
  args: ["package@version"]         # Command arguments
  env:                              # Environment variables
    VAR_NAME: "value"
  timeout: 60                       # Lambda timeout (seconds)
  memory: 1024                      # Lambda memory (MB)
```

## 🔍 Benefits of 1:1 Mapping

### **Isolation**
- Each MCP server runs independently
- Failures in one server don't affect others
- Different resource requirements per server

### **Scaling**
- Lambda scales each server based on its usage
- No resource contention between servers
- Optimal cost per server

### **Management**
- Update servers independently
- Monitor performance per server
- Easy debugging and logging

### **Security**
- Server-specific IAM permissions
- Principle of least privilege per server
- Isolated execution environments

## 🧪 Testing

### **Test All Servers Locally**
```bash
./test_multi.py
```

### **Test Individual Server**
```bash
# Test specific server via API Gateway
curl -X POST [SERVER_API_URL] \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

## 📊 Monitoring & Observability

Each Lambda function gets:
- **CloudWatch Logs**: `/aws/lambda/mcp-server-{server-id}`
- **CloudWatch Metrics**: Per-function invocation, duration, errors
- **X-Ray Tracing**: Optional distributed tracing
- **Individual Alarms**: Set up per-server monitoring

## 🔐 Security & Permissions

- Each Lambda gets minimal IAM permissions
- Server-specific permissions added automatically
- No cross-server access
- VPC isolation if needed

## 💰 Cost Optimization

- Pay per invocation per server
- No idle costs when servers aren't used
- Right-size memory and timeout per server
- Automatic scaling based on demand

## 🛠️ Development

- Python 3.9+
- AWS CDK v2
- AWS CLI configured
- YAML for configuration

## 📚 Documentation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference card with all commands and servers
- **[OVERVIEW.md](OVERVIEW.md)** - Complete project overview with all 18 servers
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Detailed deployment instructions
- **[SECURITY_NOTES.md](SECURITY_NOTES.md)** - Security configuration and best practices
- **[servers.yaml](servers.yaml)** - Central configuration for all MCP servers

## 🛠️ Management Commands

Use the management CLI for common operations:

```bash
# List all 18 configured servers
python3 manage.py list

# Check deployment status
python3 manage.py status

# Add new server interactively
python3 manage.py add

# Remove server
python3 manage.py remove

# Test specific server
python3 manage.py test eks-mcp

# Deploy all servers
python3 manage.py deploy
```

## 🎯 Quick Commands

```bash
# Generate all Lambda configurations
python3 generate_configs.py

# Test all 18 servers locally
python3 test_multi.py

# Deploy all servers to AWS
./deploy_multi.sh
```

This architecture gives you the flexibility to run 18 different MCP servers efficiently while maintaining complete isolation and optimal resource usage for AgentCore Gateway integration!

## License

MIT License