# Quick Reference - AWS Labs MCP Lambda

## 🚀 Quick Start (3 Commands)

```bash
# 1. Generate configurations for all 18 servers
python3 generate_configs.py

# 2. Test all servers locally
python3 test_multi.py

# 3. Deploy to AWS
./deploy_multi.sh
```

## 📋 18 MCP Servers Overview

| Category | Server ID | Description | Memory | Timeout |
|----------|-----------|-------------|---------|---------|
| **Core** | `core-mcp` | Core AWS functionality | 1024MB | 60s |
| **Docs** | `aws-docs` | AWS documentation search | 1024MB | 60s |
| **Cost** | `aws-pricing` | AWS pricing information | 1024MB | 60s |
| **Frontend** | `frontend-mcp` | React/web development | 1024MB | 60s |
| **Location** | `aws-location` | Geocoding and mapping | 1024MB | 60s |
| **Git** | `git-repo-research` | Advanced git analysis | 1536MB | 90s |
| **K8s** | `eks-mcp` | EKS cluster management | 2048MB | 120s |
| **Diagrams** | `aws-diagram` | Architecture diagrams | 1536MB | 90s |
| **Metrics** | `prometheus` | Prometheus monitoring | 1024MB | 60s |
| **IaC** | `cfn-mcp` | CloudFormation management | 1536MB | 90s |
| **IaC** | `terraform-mcp` | Terraform management | 2048MB | 120s |
| **Knowledge** | `aws-knowledge` | AWS knowledge base | 1024MB | 60s |
| **Logs** | `cloudwatch-mcp` | CloudWatch logs/metrics | 1536MB | 90s |
| **APM** | `cloudwatch-appsignals` | Application monitoring | 1536MB | 90s |
| **Resources** | `ccapi-mcp` | Cloud Control API | 2048MB | 120s |
| **GitHub** | `github` | GitHub operations | 1536MB | 90s |
| **Git (Legacy)** | `git-repo` | Basic git operations | 1536MB | 90s |
| **Files** | `filesystem` | File system access | 512MB | 30s |

## 🛠️ Management Commands

```bash
# List all servers
python3 manage.py list

# Check status
python3 manage.py status

# Add new server
python3 manage.py add

# Remove server
python3 manage.py remove

# Test specific server
python3 manage.py test eks-mcp

# Deploy all
python3 manage.py deploy
```

## 🔧 AgentCore Gateway Configuration

After deployment, configure each Lambda ARN:

```json
{
  "mcpServers": {
    "core-mcp": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-core-mcp"
    },
    "aws-docs": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-docs"
    }
    // ... configure all 18 servers
  }
}
```

## 🔐 Security Setup (Post-Deployment)

Set sensitive environment variables:

```bash
# GitHub token for git-repo-research
aws lambda update-function-configuration \
  --function-name mcp-server-git-repo-research \
  --environment Variables='{"GITHUB_TOKEN":"your_token_here"}'

# GitHub token for github server
aws lambda update-function-configuration \
  --function-name mcp-server-github \
  --environment Variables='{"GITHUB_PERSONAL_ACCESS_TOKEN":"your_token_here"}'
```

## 📊 Resource Allocation

- **Lightweight** (1024MB, 60s): Core, docs, pricing, frontend, location, prometheus, knowledge
- **Medium** (1536MB, 90s): Git research, diagrams, CloudFormation, CloudWatch, AppSignals, GitHub, git-repo
- **Heavy** (2048MB, 120s): EKS, Terraform, Cloud Control API
- **Minimal** (512MB, 30s): Filesystem

## 📁 Key Files

- **`servers.yaml`** - Central configuration
- **`generate_configs.py`** - Generate Lambda configs
- **`manage.py`** - Management CLI
- **`deploy_multi.sh`** - Deployment script (auto-generated)
- **`test_multi.py`** - Testing script (auto-generated)

## 🎯 Common Use Cases

- **Development**: `frontend-mcp`, `git-repo-research`, `filesystem`
- **Infrastructure**: `terraform-mcp`, `cfn-mcp`, `eks-mcp`, `ccapi-mcp`
- **Monitoring**: `cloudwatch-mcp`, `cloudwatch-appsignals`, `prometheus`
- **Documentation**: `aws-docs`, `aws-knowledge`
- **Cost Analysis**: `aws-pricing`
- **Location Services**: `aws-location`
- **Diagrams**: `aws-diagram`
- **GitHub**: `github`, `git-repo`

## 📚 Documentation

- **[README.md](README.md)** - Main documentation
- **[OVERVIEW.md](OVERVIEW.md)** - Complete project overview
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Detailed deployment
- **[SECURITY_NOTES.md](SECURITY_NOTES.md)** - Security best practices