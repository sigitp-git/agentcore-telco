# AWS AgentCore Telco Project

A comprehensive collection of specialized AWS agents built on Amazon Bedrock AgentCore, designed for telecommunications and cloud infrastructure management.

## 🏗️ Project Overview

This project contains four specialized AI agents, each tailored for specific AWS services and use cases:

- **EKS Agent** - Amazon Elastic Kubernetes Service management and troubleshooting
- **VPC Agent** - Virtual Private Cloud networking and connectivity
- **Outposts Agent** - AWS Outposts hybrid cloud infrastructure
- **Prometheus Agent** - Monitoring and observability with Amazon Managed Prometheus

## 📁 Project Structure

```
agentcore-telco/
├── .env.agents.example          # Environment template (safe to commit)
├── .env.agents                  # Actual environment (never commit)
├── .gitignore                   # Comprehensive ignore rules
├── README.md                    # Main project documentation
├── test_agents.py               # Comprehensive test suite
├── .kiro/                       # Kiro IDE configuration
│   └── steering/                # AI assistant guidance documents
│       ├── product.md           # Product overview
│       ├── tech.md              # Technology stack
│       └── structure.md         # Project structure
├── eks-agentcore/               # EKS Agent
│   ├── agent.py                 # Main agent implementation
│   ├── agent_runtime.py         # Runtime configuration
│   ├── deploy_runtime.py        # Deployment utilities
│   ├── invoke_runtime.py        # Runtime invocation interface
│   ├── select_model.py          # Model selection utility
│   ├── utils.py                 # Shared utility functions
│   ├── requirements.txt         # Agent-specific dependencies
│   ├── activate_env.sh          # Environment activation script
│   ├── run_streamlit.sh         # Streamlit launcher
│   ├── Dockerfile.runtime       # Container configuration
│   ├── LICENSE                  # License file
│   └── streamlit/               # Streamlit web application
│       ├── README.md
│       ├── demo_streamlit.py
│       ├── run_streamlit.sh
│       └── streamlit_app.py
├── vpc-agentcore/               # VPC Agent (same structure)
├── outposts-agentcore/          # Outposts Agent (same structure)
├── prometheus-agentcore/        # Prometheus Agent (same structure)
├── awslabs-mcp-lambda/          # MCP (Model Context Protocol) Integration
│   └── mcp/                     # MCP configuration and documentation
│       ├── mcp.json             # Active MCP server configuration
│       ├── mcp.json.example     # Template MCP configuration
│       ├── MCP_INTEGRATION_GUIDE.md # Comprehensive MCP integration documentation
│       └── MCP_FIXES_SUMMARY.md # Summary of MCP fixes and improvements
└── agent2agent/                 # Agent2Agent protocol integration
    ├── README.md                # A2A documentation
    ├── QUICK_START.md           # Quick start guide
    ├── types.py                 # A2A type definitions and data models
    ├── __init__.py              # Package initialization
    ├── docs/                    # Integration guides
    ├── examples/                # Example scripts
    └── wrappers/                # A2A wrapper classes
```

## 🌐 Agent2Agent (A2A) Integration

This project includes **Agent2Agent protocol integration**, enabling cross-agent communication and collaboration:

- **Enhanced Troubleshooting** - Agents collaborate for comprehensive analysis
- **Cross-Domain Context** - EKS ↔ VPC ↔ Prometheus ↔ Outposts communication
- **Automated Workflows** - Multi-agent problem resolution
- **Comprehensive Insights** - Combined analysis from multiple agents

### Quick A2A Example
```bash
# Run the A2A integration example
python3 run_a2a_example.py
```

**Key A2A Features:**
- **Agent Type System** - Complete type definitions for A2A protocol
- **Cross-Agent Messaging** - Structured communication between agents
- **Agent Cards** - Standardized capability discovery and registration
- **Enhanced Troubleshooting** - Multi-domain collaborative problem solving

See [agent2agent/README.md](agent2agent/README.md) for complete A2A documentation.

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - Primary development language
- **AWS CLI** configured with appropriate permissions
- **Access to AWS Bedrock AgentCore services**
- **Required Python packages** (installed automatically)

### Technology Stack

**Core Technologies:**
- **Amazon Bedrock AgentCore** - Agent runtime and memory management
- **AWS Systems Manager (SSM)** - Parameter store for configuration
- **AWS Cognito** - Authentication and authorization
- **strands-agents** - Core agent framework
- **boto3/botocore** - AWS SDK for Python

**Additional Libraries:**
- **ddgs** - DuckDuckGo search integration
- **fastapi/uvicorn** - Web API framework
- **streamlit** - Web UI for applications
- **requests** - HTTP client library

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd agentcore-telco
   ```

2. **Install dependencies for each agent:**
   ```bash
   # Install dependencies for all agents
   cd eks-agentcore && pip install -r requirements.txt && cd ..
   cd vpc-agentcore && pip install -r requirements.txt && cd ..
   cd outposts-agentcore && pip install -r requirements.txt && cd ..
   cd prometheus-agentcore && pip install -r requirements.txt && cd ..
   ```

3. **Configure environment:**
   ```bash
   # Copy and edit the environment file
   cp .env.agents.example .env.agents
   # Edit .env.agents with your specific configuration
   # Replace ACCOUNT_ID, REGION, RUNTIME_ID, GATEWAY_ID with actual values
   ```

4. **Verify installation:**
   ```bash
   python3 test_agents.py
   ```

## 🔧 Configuration

### Environment Variables

The `.env.agents` file contains runtime ARNs and gateway IDs for all agents:

```bash
# EKS Agent Configuration
EKS_AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/eks_agent-ID
EKS_AGENT_GATEWAY_ID=eks-agent-agentcore-gw-ID

# VPC Agent Configuration
VPC_AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/vpc_agent-ID
VPC_AGENT_GATEWAY_ID=vpc-agent-agentcore-gw-ID

# Outposts Agent Configuration
OUTPOSTS_AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/outposts_agent-ID
OUTPOSTS_AGENT_GATEWAY_ID=outposts-agent-agentcore-gw-ID

# Prometheus Agent Configuration
PROMETHEUS_AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/prometheus_agent-ID
PROMETHEUS_AGENT_GATEWAY_ID=prometheus-agent-agentcore-gw-ID
```

### MCP (Model Context Protocol) Configuration

The project includes comprehensive MCP integration with AWS services through the `awslabs-mcp-lambda/mcp/mcp.json` configuration file:

```json
{
    "mcpServers": {
        "awslabs.core-mcp-server": {
            "command": "uvx",
            "args": ["awslabs.core-mcp-server@latest"],
            "env": {
                "FASTMCP_LOG_LEVEL": "ERROR",
                "AWS_DEFAULT_REGION": "us-east-1",
                "AWS_REGION": "us-east-1"
            },
            "disabled": false,
            "autoApprove": []
        },
        "awslabs.prometheus-mcp-server": {
            "command": "uvx",
            "args": [
                "awslabs.prometheus-mcp-server@latest",
                "--url", "https://aps-workspaces.us-east-1.amazonaws.com/workspaces/WORKSPACE_ID",
                "--region", "us-east-1"
            ],
            "env": {
                "FASTMCP_LOG_LEVEL": "ERROR",
                "AWS_DEFAULT_REGION": "us-east-1",
                "AWS_REGION": "us-east-1"
            },
            "disabled": false,
            "autoApprove": ["GetAvailableWorkspaces", "ListMetrics", "ExecuteQuery"]
        }
    }
}
```

**Available MCP Servers (52 tools total):**
- **core** (1 tool) - Core MCP functionality
- **aws-documentation** (3 tools) - AWS documentation search and retrieval
- **eks** (16 tools) - EKS cluster management and Kubernetes operations
- **prometheus** (5 tools) - Prometheus metrics and query execution
- **aws-knowledge** (3 tools) - AWS knowledge base integration
- **cloudwatch** (10 tools) - CloudWatch logs, metrics, and alarms
- **ccapi** (14 tools) - AWS Cloud Control API for resource management

📚 **For detailed MCP integration information, see:**
- [MCP Integration Guide](awslabs-mcp-lambda/mcp/MCP_INTEGRATION_GUIDE.md) - Comprehensive setup and troubleshooting
- [MCP Fixes Summary](awslabs-mcp-lambda/mcp/MCP_FIXES_SUMMARY.md) - Recent improvements and fixes

### SSM Parameters

Each agent requires specific SSM parameters for authentication and configuration:

#### EKS Agent
- `/app/eksagent/agentcore/machine_client_id`
- `/app/eksagent/agentcore/cognito_auth_scope`
- `/app/eksagent/agentcore/cognito_token_url`
- `/app/eksagent/agentcore/runtime_arn`

#### VPC Agent
- `/app/vpcagent/agentcore/machine_client_id`
- `/app/vpcagent/agentcore/cognito_auth_scope`
- `/app/vpcagent/agentcore/cognito_token_url`
- `/app/vpcagent/agentcore/runtime_arn`

#### Outposts Agent
- `/app/outpostsagent/agentcore/machine_client_id`
- `/app/outpostsagent/agentcore/cognito_auth_scope`
- `/app/outpostsagent/agentcore/cognito_token_url`
- `/app/outpostsagent/agentcore/runtime_arn`

#### Prometheus Agent
- `/app/prometheusagent/agentcore/machine_client_id`
- `/app/prometheusagent/agentcore/cognito_auth_scope`
- `/app/prometheusagent/agentcore/cognito_token_url`
- `/app/prometheusagent/agentcore/runtime_arn`

## 🎯 Agent Capabilities

### EKS Agent
- **Cluster Management**: Create, configure, and manage EKS clusters
- **Node Group Operations**: Manage worker nodes and auto-scaling
- **Troubleshooting**: Diagnose and resolve EKS-related issues
- **Security**: Configure RBAC, security groups, and IAM roles
- **Monitoring**: Integration with CloudWatch and container insights

### VPC Agent
- **Network Architecture**: Design and implement VPC topologies
- **Connectivity**: Configure VPN, Direct Connect, and peering
- **Security Groups**: Manage firewall rules and network ACLs
- **Routing**: Configure route tables and traffic flow
- **Troubleshooting**: Network connectivity and performance issues

### Outposts Agent
- **Hybrid Infrastructure**: Manage on-premises AWS Outposts
- **Capacity Planning**: Monitor and optimize resource utilization
- **Connectivity**: Ensure reliable connection to AWS regions
- **Local Services**: Configure and manage local AWS services
- **Maintenance**: Coordinate updates and maintenance windows

### Prometheus Agent
- **Metrics Collection**: Configure Prometheus data sources and Amazon Managed Prometheus
- **Query Optimization**: Write and optimize PromQL queries with real-time execution
- **MCP Integration**: 52 AWS MCP tools for comprehensive AWS service integration
- **Workspace Management**: Automatic detection and management of Prometheus workspaces
- **Real-time Queries**: Execute PromQL queries against live Prometheus instances
- **Alerting**: Set up and manage alert rules and notification channels
- **Visualization**: Integration with Grafana and custom dashboards
- **Troubleshooting**: Diagnose monitoring, alerting, and MCP integration issues
- **AWS Services**: Direct integration with EKS, CloudWatch, and AWS documentation

## 🛠️ Usage

### Running Individual Agents

Each agent can be run independently:

```bash
# EKS Agent
cd eks-agentcore
python3 agent.py

# VPC Agent
cd vpc-agentcore
python3 agent.py

# Outposts Agent
cd outposts-agentcore
python3 agent.py

# Prometheus Agent
cd prometheus-agentcore
python3 agent.py
```

### Using Runtime Invocation

For programmatic access, use the runtime invoker:

```bash
# Interactive mode
cd eks-agentcore
python3 invoke_runtime.py interactive

# Test mode
python3 invoke_runtime.py test

# Direct invocation
python3 invoke_runtime.py
```

### Model Selection

Each agent supports multiple Claude models. To change the model:

```bash
cd eks-agentcore
python3 agent.py --select-model
```

Available models:
- **Claude Sonnet 4** - Latest, most capable
- **Claude 3.7 Sonnet** - Enhanced reasoning
- **Claude 3.5 Sonnet v2** - Balanced performance
- **Claude 3.5 Sonnet v1** - Stable version
- **Claude 3.5 Haiku** - Fast & efficient (default)

### Streamlit Web Interface

Each agent includes a modern web interface built with Streamlit:

```bash
# Launch web interface for any agent
cd eks-agentcore/streamlit
./run_streamlit.sh

# Or from the agent root directory
cd eks-agentcore
./run_streamlit.sh
```

Features:
- 🎨 Modern AWS-themed web interface
- 💬 Real-time chat with agents
- 🤖 Interactive model selector
- 📋 Pre-built example prompts
- 🔄 Session management controls
- 📱 Mobile-friendly responsive design

Access at: http://localhost:8501

## 🔄 Recent Updates

### MCP Tools Integration Fixes (Latest)
- ✅ **Fixed MCP Loading**: Resolved MCP tools not loading from mcp.json configuration
- ✅ **Eliminated Duplicate Output**: Fixed verbose logging causing duplicate responses
- ✅ **Enhanced Logging Control**: Added comprehensive logging suppression for clean output
- ✅ **52 AWS MCP Tools**: Successfully loading all MCP servers (core, aws-documentation, eks, prometheus, aws-knowledge, cloudwatch, ccapi)
- ✅ **Prometheus Agent**: Full MCP integration with Amazon Managed Prometheus

### Agent2Agent Integration Fixes
- ✅ **Fixed Import Issues**: Resolved `ModuleNotFoundError: No module named 'a2a'`
- ✅ **Complete Type System**: Added comprehensive `agent2agent.types` module
- ✅ **Protocol Validation**: Type-safe A2A communication with validation
- ✅ **Enhanced Documentation**: Updated all A2A documentation and examples
- ✅ **Working Examples**: All A2A integration examples now run successfully

### Key Improvements
- **MCP Integration**: Full Model Context Protocol support with 52 AWS tools
- **Clean Output**: Eliminated duplicate logging and verbose MCP server output
- **Type Safety**: Full type definitions for AgentCard, Message, Capabilities
- **Error Handling**: Proper validation and error messages for A2A types
- **Documentation**: Complete documentation updates across all modules
- **Testing**: Verified A2A integration works end-to-end

## 🧪 Testing

### Comprehensive Test Suite

Run the complete test suite to validate all agents:

```bash
python3 test_agents.py
```

The test suite validates:
- ✅ **Agent Import**: Python module loading and configuration
- ✅ **Runtime Functionality**: AgentRuntimeInvoker and ARN configuration
- ✅ **Token Authentication**: Cognito authentication and access tokens
- ✅ **Error Handling**: Graceful degradation and error reporting

### Expected Test Output

```
🧪 COMPREHENSIVE AGENT TEST SUITE
==================================================

🎯 AGENT STATUS SUMMARY
----------------------------------------
EKS          | agent.py: ✅ | runtime: ✅ | token: ✅ | 🟢 EXCELLENT
VPC          | agent.py: ✅ | runtime: ✅ | token: ✅ | 🟢 EXCELLENT
OUTPOSTS     | agent.py: ✅ | runtime: ✅ | token: ✅ | 🟢 EXCELLENT
PROMETHEUS   | agent.py: ✅ | runtime: ✅ | token: ✅ | 🟢 EXCELLENT

Total Core Tests: 8
Passed: 8 ✅
Failed: 0 ❌
Success Rate: 100.0%

🎉 ALL CORE TESTS PASSED! All agents are fully functional.
```

## 🔐 Security & Authentication

### Cognito Authentication
All agents use AWS Cognito for secure authentication:
- Machine-to-machine authentication via client credentials
- Scoped access tokens for MCP gateway communication
- Automatic token refresh and error handling

### IAM Permissions
Required IAM permissions for each agent:
- **EKS Agent**: EKS cluster management, EC2 instances, IAM roles
- **VPC Agent**: VPC management, networking resources, security groups
- **Outposts Agent**: Outposts management, local resource access
- **Prometheus Agent**: Managed Prometheus, CloudWatch metrics

### SSM Parameter Store
Sensitive configuration stored securely in AWS Systems Manager:
- Client IDs and authentication scopes
- Runtime ARNs and gateway configurations
- Encrypted storage with appropriate access controls

## 📊 Monitoring & Observability

### Built-in Features
- **Structured Logging**: Comprehensive logging with different levels
- **Error Tracking**: Detailed error capture and reporting
- **Performance Metrics**: Execution time and resource usage
- **Health Checks**: Automatic validation of agent functionality

### Integration Points
- **CloudWatch Logs**: Centralized log aggregation
- **CloudWatch Metrics**: Custom metrics and dashboards
- **AWS X-Ray**: Distributed tracing for complex operations
- **Amazon Managed Prometheus**: Metrics collection and alerting

## 🚨 Troubleshooting

### Common Issues

#### Agent Import Failures
```bash
# Check Python path and dependencies
cd eks-agentcore
python3 -c "import sys; print(sys.path)"
pip install -r requirements.txt
```

#### Authentication Errors
```bash
# Verify SSM parameters
aws ssm get-parameters-by-path --path "/app/eksagent/agentcore" --recursive

# Check AWS credentials
aws sts get-caller-identity
```

#### Runtime ARN Issues
```bash
# Validate environment configuration
cat .env.agents
python3 -c "from dotenv import load_dotenv; load_dotenv('.env.agents'); import os; print(os.environ.get('EKS_AGENT_RUNTIME_ARN'))"
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
export PYTHONPATH=.
export AWS_DEFAULT_REGION=us-east-1
export DEBUG=true
python3 agent.py
```

### Log Analysis

Check agent logs for issues:
```bash
# CloudWatch Logs
aws logs describe-log-groups --log-group-name-prefix "/aws/bedrock/agentcore"

# Local logs
tail -f agent.log
```

## 🤖 AI Assistant Integration

### Kiro Steering Documents

The project includes AI assistant guidance documents in `.kiro/steering/`:

- **`product.md`** - Product overview and target users
- **`tech.md`** - Technology stack and build commands  
- **`structure.md`** - Project organization and conventions

These documents help AI assistants understand the project context, coding standards, and architectural patterns when working with the codebase.

## 🔄 Development

### Adding New Agents

1. **Create agent directory:**
   ```bash
   mkdir new-agent-agentcore
   cd new-agent-agentcore
   ```

2. **Copy template files:**
   ```bash
   cp ../eks-agentcore/agent.py .
   cp ../eks-agentcore/invoke_runtime.py .
   cp ../eks-agentcore/utils.py .
   ```

3. **Update configuration:**
   - Modify agent.py with specific functionality
   - Update SSM parameter paths
   - Add environment variables to .env.agents

4. **Test the new agent:**
   ```bash
   # Add to test_agents.py
   python3 test_agents.py
   ```

### Code Standards

- **Python 3.8+** compatibility
- **Type hints** for better code clarity
- **Docstrings** for all functions and classes
- **Error handling** with graceful degradation
- **Logging** for debugging and monitoring

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## 📚 Additional Resources

### Project Documentation
- [MCP Integration Guide](awslabs-mcp-lambda/mcp/MCP_INTEGRATION_GUIDE.md) - Complete MCP setup and troubleshooting
- [MCP Fixes Summary](awslabs-mcp-lambda/mcp/MCP_FIXES_SUMMARY.md) - Recent MCP improvements and fixes
- [Agent2Agent Documentation](agent2agent/README.md) - Cross-agent communication protocol

### External Resources
- [AWS Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude 3.5 Model Documentation](https://docs.anthropic.com/claude/docs)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the test suite output for diagnostic information

---

**Built with ❤️ for AWS telecommunications and cloud infrastructure teams**