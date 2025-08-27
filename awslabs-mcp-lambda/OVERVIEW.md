# AWS Labs MCP Lambda - Complete Overview

## 🎯 Project Summary

This project provides a **complete Lambda-based infrastructure** for running **18 different MCP (Model Context Protocol) servers** on AWS Lambda with **1:1 mapping** - one dedicated Lambda function per MCP server. Designed specifically for integration with **Amazon Bedrock AgentCore Gateway**.

## 📊 Current Configuration (18 MCP Servers)

### **AWS Labs MCP Servers (15 servers)**

| Server ID | Name | Description | Memory | Timeout |
|-----------|------|-------------|---------|---------|
| `core-mcp` | AWS Labs Core MCP Server | Core AWS functionality and prompt understanding | 1024MB | 60s |
| `aws-pricing` | AWS Pricing MCP Server | AWS service pricing information and cost analysis | 1024MB | 60s |
| `aws-docs` | AWS Documentation MCP Server | Search and retrieve AWS documentation | 1024MB | 60s |
| `frontend-mcp` | AWS Labs Frontend MCP Server | React/frontend development tools | 1024MB | 60s |
| `aws-location` | AWS Location MCP Server | AWS Location Service for geocoding and mapping | 1024MB | 60s |
| `git-repo-research` | Git Repository Research MCP Server | Advanced git repository analysis and research | 1536MB | 90s |
| `eks-mcp` | AWS EKS MCP Server | Amazon EKS cluster management and troubleshooting | 2048MB | 120s |
| `aws-diagram` | AWS Diagram MCP Server | Generate AWS architecture diagrams | 1536MB | 90s |
| `prometheus` | Prometheus MCP Server | Prometheus metrics and monitoring | 1024MB | 60s |
| `cfn-mcp` | AWS CloudFormation MCP Server | CloudFormation template management | 1536MB | 90s |
| `terraform-mcp` | Terraform MCP Server | Terraform infrastructure management | 2048MB | 120s |
| `aws-knowledge` | AWS Knowledge MCP Server | AWS Knowledge base via proxy | 1024MB | 60s |
| `cloudwatch-mcp` | AWS CloudWatch MCP Server | CloudWatch logs and metrics analysis | 1536MB | 90s |
| `cloudwatch-appsignals` | AWS CloudWatch Application Signals MCP Server | Application monitoring and observability | 1536MB | 90s |
| `ccapi-mcp` | AWS Cloud Control API MCP Server | AWS resource management via Cloud Control API | 2048MB | 120s |

### **Third-party MCP Servers (3 servers)**

| Server ID | Name | Description | Memory | Timeout |
|-----------|------|-------------|---------|---------|
| `github` | GitHub MCP Server | GitHub repository and issue management | 1536MB | 90s |
| `git-repo` | Git Repository MCP Server (Legacy) | Basic git repository operations | 1536MB | 90s |
| `filesystem` | Filesystem MCP Server | File system operations (Lambda /tmp only) | 512MB | 30s |

## 🏗️ Architecture Benefits

### **1:1 Mapping Advantages**
- **Isolation**: Each MCP server runs in its own Lambda function
- **Independent Scaling**: Each server scales based on its own usage patterns
- **Resource Optimization**: Right-sized memory and timeout per server
- **Cost Efficiency**: Pay only for what each server uses
- **Security**: Server-specific IAM permissions and isolation

### **AgentCore Gateway Integration**
- **Direct Lambda Invocation**: No API Gateway needed for AgentCore
- **JSON-RPC 2.0 Compliant**: Full MCP protocol support
- **Individual ARNs**: Each server gets its own Lambda ARN for configuration

## 🔐 Security Features

### **IAM Permissions by Server Type**
- **EKS MCP**: EKS cluster access, CloudWatch logs
- **CloudWatch MCP**: CloudWatch read permissions, log analysis
- **CloudWatch AppSignals**: Application Signals and X-Ray permissions
- **Prometheus**: Amazon Managed Prometheus access
- **CloudFormation**: CloudFormation read/write permissions
- **Terraform**: S3 state bucket and DynamoDB lock table access
- **AWS Location**: Location Service geocoding permissions
- **Cloud Control API**: Broad AWS resource management permissions
- **Others**: Minimal permissions as needed

### **Sensitive Data Handling**
- **GitHub Tokens**: Configured via Lambda environment variables (not hardcoded)
- **AWS Credentials**: Use Lambda execution roles (no hardcoded keys)
- **Secrets Manager Integration**: Ready for production secret management

## 📁 Project Structure

```
awslabs-mcp-lambda/
├── README.md                    # Main documentation
├── DEPLOYMENT_GUIDE.md          # Detailed deployment instructions
├── SECURITY_NOTES.md            # Security configuration guide
├── OVERVIEW.md                  # This file - complete overview
├── servers.yaml                 # Central configuration for all 18 servers
├── requirements.txt             # CDK dependencies
├── app.py                      # Multi-Lambda CDK application
├── generate_configs.py         # Generate per-server Lambda configurations
├── manage.py                   # Management CLI tool
├── deploy_multi.sh             # Deployment script (auto-generated)
├── test_multi.py               # Testing script (auto-generated)
├── lambda/                     # Base Lambda code template
│   ├── handler.py             # Lambda handler
│   ├── mcp_wrapper.py         # MCP server wrapper
│   ├── config.py              # Server configuration template
│   └── requirements.txt       # Lambda runtime dependencies
├── lambda-{server-id}/         # Generated per-server Lambda code (18 directories)
├── infrastructure/
│   ├── lambda_stack.py        # Single Lambda stack (legacy)
│   └── multi_lambda_stack.py  # Multi-Lambda CDK stack
└── tests/
    └── test_mcp_server.py     # Unit tests
```

## 🚀 Deployment Process

### **1. Pre-configured Setup**
The project comes with all 18 MCP servers pre-configured. No manual setup required.

### **2. Generate Configurations**
```bash
python3 generate_configs.py
```
Creates 18 individual Lambda directories with server-specific configurations.

### **3. Test Locally**
```bash
python3 test_multi.py
```
Tests all 18 servers locally before deployment.

### **4. Deploy to AWS**
```bash
./deploy_multi.sh
```
Deploys all 18 Lambda functions with proper IAM permissions.

### **5. Configure AgentCore Gateway**
Use the 18 Lambda ARNs in your AgentCore Gateway configuration.

## 🛠️ Management Tools

### **Management CLI**
```bash
# List all configured servers
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

### **Generated Scripts**
- **`deploy_multi.sh`**: Automated deployment script
- **`test_multi.py`**: Comprehensive testing script

## 💰 Cost Optimization

### **Resource Allocation Strategy**
- **Lightweight servers** (docs, pricing): 1024MB, 60s timeout
- **Medium servers** (git, cloudwatch): 1536MB, 90s timeout  
- **Heavy servers** (eks, terraform, ccapi): 2048MB, 120s timeout
- **Minimal server** (filesystem): 512MB, 30s timeout

### **Pay-per-Use Model**
- No idle costs when servers aren't used
- Independent scaling per server
- Automatic resource optimization

## 📊 Monitoring & Observability

### **Per-Server Monitoring**
- **CloudWatch Logs**: `/aws/lambda/mcp-server-{server-id}`
- **CloudWatch Metrics**: Invocations, duration, errors, memory usage
- **Individual Alarms**: Set up per-server monitoring
- **Cost Tracking**: Per-server cost breakdown

### **Centralized Management**
- Single deployment for all servers
- Unified configuration management
- Consistent security policies

## 🔄 Maintenance & Updates

### **Individual Server Updates**
- Update specific servers without affecting others
- Independent versioning per server
- Rollback capabilities per server

### **Bulk Operations**
- Update all servers at once
- Consistent configuration across servers
- Automated testing before deployment

## 🎯 Use Cases

### **Development Teams**
- **Frontend developers**: Use `frontend-mcp` for React/web development
- **Infrastructure teams**: Use `terraform-mcp`, `cfn-mcp`, `eks-mcp`
- **DevOps teams**: Use `cloudwatch-mcp`, `prometheus`, monitoring servers
- **Security teams**: Use `ccapi-mcp` for resource compliance

### **AI/ML Workflows**
- **Documentation**: `aws-docs` for AWS service information
- **Cost analysis**: `aws-pricing` for cost optimization
- **Code analysis**: `git-repo-research` for repository insights
- **Infrastructure**: `terraform-mcp`, `cfn-mcp` for IaC management

## 🚨 Important Notes

### **Security Considerations**
1. **GitHub tokens** must be set via Lambda environment variables
2. **AWS credentials** use Lambda execution roles (no hardcoded keys)
3. **Production deployments** should use AWS Secrets Manager
4. **IAM permissions** are server-specific and follow least privilege

### **Resource Limits**
- **Docker-based servers** (GitHub) may have longer cold start times
- **Heavy servers** (EKS, Terraform) allocated more resources
- **Lambda limits** apply (15-minute max execution, 10GB max memory)

### **AgentCore Gateway Integration**
- Each server gets its own Lambda ARN
- Direct Lambda invocation (no API Gateway needed)
- JSON-RPC 2.0 compliant responses
- Proper error handling and logging

This comprehensive setup provides a production-ready, scalable, and secure foundation for running multiple MCP servers in a serverless environment with Amazon Bedrock AgentCore Gateway integration.