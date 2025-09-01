# AWS AgentCore Telco Project

A comprehensive collection of specialized AWS agents built on Amazon Bedrock AgentCore, designed for telecommunications and cloud infrastructure management.

## 🏗️ Project Overview

This project contains four specialized AI agents, each tailored for specific AWS services and use cases:

- **EKS Agent** - Amazon Elastic Kubernetes Service management and troubleshooting
- **VPC Agent** - Virtual Private Cloud networking and connectivity
- **Outposts Agent** - AWS Outposts hybrid cloud infrastructure
- **Prometheus Agent** - Monitoring and observability with Amazon Managed Prometheus

### Telecommunications Multi-Agent Architecture

The project implements a sophisticated multi-agent collaboration pattern specifically designed for telecommunications infrastructure management. Each telco network function (UPF, AMF, SMF, vCU, vDU) is paired with intelligent agentic sidecars that communicate with our specialized AWS agents for comprehensive infrastructure management.

📋 **Architecture details are included in the Agent Capabilities & Architecture section below.**

## 📁 Project Structure

```
agentcore-telco/
├── .env.agents.example          # Environment template (safe to commit)
├── .env.agents                  # Actual environment (never commit)
├── .gitignore                   # Comprehensive ignore rules
├── README.md                    # Main project documentation
├── LICENSE                      # MIT License for the entire project
├── test_agents.py               # Comprehensive test suite
├── .kiro/                       # Kiro IDE configuration
│   └── steering/                # AI assistant guidance documents
│       ├── product.md           # Product overview
│       ├── tech.md              # Technology stack
│       └── structure.md         # Project structure
├── docs/                        # Documentation
│   ├── AGENT_IMPROVEMENTS.md    # Consolidated agent improvements and technical details
│   ├── DOCUMENTATION_CONSOLIDATION_SUMMARY.md # Documentation consolidation summary
│   └── telco-architecture-pattern.md # Telco architecture patterns
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
│   └── streamlit/               # Streamlit web application
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

# Or run directly
python3 agent2agent/examples/a2a_integration_example_full.py
```

**Key A2A Features:**
- **Agent Type System** - Complete type definitions for A2A protocol
- **Cross-Agent Messaging** - Structured communication between agents
- **Agent Cards** - Standardized capability discovery and registration
- **Enhanced Troubleshooting** - Multi-domain collaborative problem solving

#### A2A Usage in Your Code

```python
# Import A2A types for protocol communication
from agent2agent.types import (
    AgentCard, AgentCapabilities, AgentSkill, Message, TextPart, Role
)

# Import the EKS A2A wrapper
from agent2agent.wrappers.eks_a2a_wrapper import EKSA2AWrapper

# Create wrapper for your EKS agent
eks_agent = YourEKSAgent()
a2a_wrapper = EKSA2AWrapper(eks_agent)

# Enhanced troubleshooting with cross-agent collaboration
result = await a2a_wrapper.enhanced_pod_troubleshooting(
    pod_name="web-app-123",
    namespace="production", 
    cluster_name="prod-cluster"
)
```

#### Cross-Agent Communication

```python
# Request VPC analysis
vpc_response = await a2a_wrapper.send_request_to_agent("VPC-Agent", {
    "action": "analyze_network_connectivity",
    "vpc_id": "vpc-prod-123"
})

# Request metrics from Prometheus
metrics = await a2a_wrapper.send_request_to_agent("Prometheus-Agent", {
    "action": "get_cluster_metrics",
    "cluster_name": "prod-cluster"
})
```

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
- [MCP Lambda Documentation](awslabs-mcp-lambda/README.md) - Serverless MCP deployment guide
- [Library Overview](awslabs-mcp-lambda/LIBRARY_OVERVIEW.md) - Technical details of the MCP Lambda library
- [Deployment Status](awslabs-mcp-lambda/DEPLOYMENT_SUCCESS.md) - Current deployment status and results

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

## 🎯 Agent Capabilities & Architecture

### System Architecture Overview

The AWS AgentCore Telco project implements a multi-agent architecture designed for telecommunications and cloud infrastructure management. The system consists of specialized AI agents that collaborate to provide comprehensive AWS infrastructure management.

#### Communication Patterns

1. **Agent-to-AgentCore Communication**
   ```
   Agent ←→ AgentCore Runtime ←→ Memory Service
     ↓
   Gateway ←→ MCP Servers ←→ AWS Services
   ```

2. **Cross-Agent Communication (A2A)**
   ```
   EKS Agent ←→ A2A Protocol ←→ VPC Agent
       ↓                           ↓
   Prometheus Agent ←→ A2A ←→ Outposts Agent
   ```

3. **MCP Integration Architecture**
   ```
   Agent ←→ MCP Client ←→ MCP Server ←→ AWS Service
                    ↓
               Lambda Function (Serverless)
                    ↓
               AWS Service API
   ```

### Agent Capabilities

**🏗️ All agents now use identical MCP-only architecture for consistent, scalable operations**

#### EKS Agent
- **Cluster Management**: Create, configure, and manage EKS clusters with advanced configuration
- **Node Group Operations**: Manage worker nodes, scaling policies, and instance types
- **MCP-Only Architecture**: All AWS operations use MCP tools exclusively (AgentCore Gateway + AWS MCP servers)
- **Kubernetes Integration**: Deploy applications, manage services, and troubleshoot workloads
- **Security Configuration**: RBAC, security groups, and IAM role management
- **Monitoring Setup**: CloudWatch integration and logging configuration
- **Troubleshooting**: Diagnose cluster issues, pod failures, and networking problems
- **Cost Optimization**: Right-sizing recommendations and resource efficiency analysis
- **Enhanced Reliability**: Robust error handling with timeout protection and graceful exit

#### VPC Agent
- **Network Architecture**: Design and implement VPC topologies with MCP-only operations
- **Connectivity**: Configure VPN, Direct Connect, and peering through AWS MCP tools
- **Security Groups**: Manage firewall rules and network ACLs with enhanced automation
- **Routing**: Configure route tables and traffic flow optimization
- **Troubleshooting**: Network connectivity and performance issue resolution
- **Cross-Agent Integration**: Collaborate with EKS and Outposts agents for comprehensive analysis
- **MCP-Only Architecture**: All AWS operations use MCP tools exclusively for better scalability

#### Outposts Agent
- **Hybrid Infrastructure**: Manage on-premises AWS Outposts with MCP-based operations
- **Capacity Planning**: Monitor and optimize resource utilization through AWS MCP tools
- **Connectivity**: Ensure reliable connection to AWS regions with automated diagnostics
- **Local Services**: Configure and manage local AWS services on Outposts
- **Maintenance**: Coordinate updates and maintenance windows with enhanced scheduling
- **Telco Integration**: Specialized support for 5G network functions and edge computing
- **MCP-Only Architecture**: All AWS operations use MCP tools exclusively for consistency

#### Prometheus Agent
- **Metrics Collection**: Configure Prometheus data sources and Amazon Managed Prometheus
- **Query Optimization**: Write and optimize PromQL queries with real-time execution
- **MCP-Only Architecture**: All AWS operations use MCP tools exclusively (AgentCore Gateway + AWS MCP servers)
- **Workspace Management**: Automatic detection and management of Prometheus workspaces
- **Real-time Queries**: Execute PromQL queries against live Prometheus instances
- **Alerting**: Set up and manage alert rules and notification channels
- **Visualization**: Integration with Grafana and custom dashboards
- **Troubleshooting**: Diagnose monitoring, alerting, and MCP integration issues
- **AWS Services**: Direct integration with EKS, CloudWatch, and AWS documentation through MCP tools
- **Enhanced Reliability**: Robust error handling with timeout protection and graceful exit

### Telco Multi-Agent Collaboration Pattern

#### 5G Network Function Integration
The architecture supports 5G network functions through intelligent sidecars:

**5G Core Functions:**
- **UPF (User Plane Function)**: Data traffic routing
- **AMF (Access and Mobility Management)**: Device registration and mobility
- **SMF (Session Management Function)**: Session management
- **vCU (Centralized Unit)**: RAN Layer 2/3 functions
- **vDU (Distributed Unit)**: RAN Layer 1/2 functions

**Agentic Sidecars:**
Each telco container is paired with an intelligent sidecar that:
- Monitors container health and performance
- Communicates with AWS agents for infrastructure management
- Provides correlation between telco functions and AWS services
- Enables automated remediation and optimization

#### Communication Flow
1. **Telco Container ↔ Agentic Sidecar**: 1:1 pairing for health monitoring
2. **Agentic Sidecar ↔ AWS Agents**: Many-to-many for infrastructure management
3. **AWS Agent ↔ AgentCore Gateway**: 1:1 dedicated connection for tool execution

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

### Runtime Deployment

Each agent includes a comprehensive deployment system with standardized `deploy_runtime.py` scripts:

```bash
# Deploy agent to AgentCore Runtime
cd eks-agentcore
python3 deploy_runtime.py

# Deploy with options
python3 deploy_runtime.py --region us-west-2
python3 deploy_runtime.py --skip-build
python3 deploy_runtime.py --test-only
python3 deploy_runtime.py --help-extended
```

**Deployment Features:**
- ✅ **Automated ECR Management** - Creates repositories when needed
- ✅ **Docker Build & Push** - Handles containerization automatically
- ✅ **Runtime Updates** - Updates existing runtimes with confirmation
- ✅ **Region Configuration** - Supports multi-region deployment
- ✅ **SSM Integration** - Manages execution roles and parameters
- ✅ **Error Handling** - Comprehensive validation and recovery

**Runtime Testing:**
```bash
# Test runtime functionality
python3 invoke_runtime.py interactive

# Test mode
python3 invoke_runtime.py test

# Direct invocation
python3 invoke_runtime.py
```

#### Bedrock AgentCore Runtime Architecture

All agents follow a standardized Bedrock AgentCore runtime pattern:

**Key Features:**
- **Memory Mandatory**: All runtime agents use persistent memory for context retention
- **MCP Configuration Disabled**: Runtime environment disables MCP configuration since we can't install packages on runtime. Runtime agents will use AgentCore Gateway MCP server(s) instead
- **System Prompt Constants**: Each agent uses a dedicated system prompt constant (e.g., `EKS_SYSTEM_PROMPT`, `PROMETHEUS_SYSTEM_PROMPT`)
- **Initialization Functions**: Standardized `initialize_runtime_components()`, `setup_gateway_and_mcp()`, and `setup_memory()` functions
- **Error Handling**: Robust error handling with graceful degradation

**Runtime Configuration:**
```python
# MCP settings are automatically disabled for runtime
AgentConfig.ENABLE_MCP_CONFIG = False
AgentConfig.ENABLE_AWS_MCP = False

# Runtime components initialization
model, memory_id, memory_client, mcp_client = agent.initialize_runtime_components()

# Agent creation with system prompt constant
runtime_agent = Agent(
    model=model,
    tools=tools,
    hooks=hooks,
    system_prompt=AgentConfig.EKS_SYSTEM_PROMPT  # Agent-specific constant
)
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

### Model Configuration

All agents are optimized with the following model settings:
- **Temperature: 0.3** - Deterministic responses for consistent troubleshooting
- **Max Tokens: 4096** - Sufficient for detailed analysis and comprehensive responses
- **Top-P: 0.9** - Balanced creativity for problem-solving while maintaining technical accuracy

NOTE:
> Top-p and top-k are two different sampling strategies used in Amazon Bedrock models to control text generation:

Top-k sampling:
• Limits the model to consider only the k most likely next tokens
• Example: If top-k = 50, only the 50 most probable tokens are considered
• Creates a fixed-size pool of candidates regardless of their probability distribution
• Can include very low-probability tokens if they're in the top k

Top-p sampling (nucleus sampling):
• Selects tokens from the smallest set whose cumulative probability exceeds the threshold p
• Example: If top-p = 0.9, tokens are selected until their combined probability reaches 90%
• Creates a dynamic pool size based on probability distribution
• Automatically excludes very low-probability tokens

Key differences:

• **Flexibility**: Top-p adapts to the probability distribution, while top-k uses a fixed number
• **Quality**: Top-p typically produces more coherent text by avoiding unlikely tokens
• **Predictability**: Top-k gives consistent candidate pool sizes, top-p varies based on context

In Bedrock:
• Most models support both parameters
• You can use them together (top-k filters first, then top-p)
• Common values: top-p = 0.9-0.95, top-k = 40-100
• Lower values = more focused/deterministic output
• Higher values = more creative/diverse output

For most use cases, top-p alone (around 0.9) provides good results. Combine both when you need fine-grained control over the generation process.

These settings are specifically tuned for infrastructure management tasks, providing reliable and detailed responses for complex AWS operations.

### Streamlit Web Interface

Each agent includes a modern web interface built with Streamlit:

```bash
# Launch web interface for any agent
cd eks-agentcore/streamlit
./run_streamlit.sh

# Or from the agent root directory
cd eks-agentcore
./run_streamlit.sh

# Manual launch (from streamlit directory)
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

**Features:**
- 🎨 Modern AWS-themed web interface
- 💬 Real-time chat with agents
- 🤖 Interactive model selector with 5 Claude models
- 📋 Pre-built example prompts
- 🔄 Session management controls
- 📱 Mobile-friendly responsive design
- ⚡ Direct integration with AgentCore Runtime
- 🔧 Real-time model switching with visual feedback

**Access:** http://localhost:8501 (local) or http://your-ip:8501 (network)

**Requirements:**
- Python 3.8+
- Streamlit >= 1.28.0
- AWS credentials configured
- Access to deployed AWS Agent

**Files in each agent's streamlit/ directory:**
- `streamlit_app.py` - Main Streamlit application
- `run_streamlit.sh` - Launch script for the Streamlit app
- `demo_streamlit.py` - Demo script showcasing features

## 📋 Version History & Agent Improvements

**🎉 PROJECT MILESTONE: MCP-Only Architecture Completed (September 2025)**

All four agents (VPC, Outposts, EKS, Prometheus) have been successfully refactored to use identical MCP-only architecture, providing consistent, scalable, and maintainable AWS operations across the entire telco agent ecosystem.

### Latest (September 2025)

#### 🏗️ MCP-Only Architecture Completion ✅
- **Complete Architecture Refactoring**: All four agents (VPC, Outposts, EKS, Prometheus) now use identical MCP-only architecture
  - ✅ **Removed all hardcoded boto3 tools** from all agents (`list_eks_clusters`, `aws_resource_guidance`, `eks_tool_guidance`)
  - ✅ **All AWS operations use MCP tools exclusively** (AgentCore Gateway + AWS MCP servers)
  - ✅ **Consistent tool discovery and help systems** across all agents with unified `/tools` command
  - ✅ **Enhanced error handling** with user-friendly messages and clean MCP integration
  - ✅ **Updated system prompts** for all agents to reflect MCP-only architecture
  - ✅ **Fixed MCP configuration logic** distinguishing AgentCore Gateway vs AWS MCP modes
  - ✅ **Cleaned user-facing text** removing technical 'stdio' references
- **Architecture Benefits Achieved**: 
  - **Better Scalability**: New AWS services automatically available through MCP servers
  - **Improved Maintainability**: No hardcoded AWS SDK calls to maintain across 4 agents
  - **Enhanced User Experience**: Clean error messages, tool discovery, and consistent interfaces
  - **Future-Proof Design**: Ready for new MCP servers and AWS services without code changes
  - **Architectural Consistency**: All agents follow identical patterns for reliability

#### ✨ Previous Features (August 2025)
- **Standardized Runtime Deployment**: Complete `deploy_runtime.py` system across all agents
  - Automated ECR repository management with creation when needed
  - Docker build and push with comprehensive error handling
  - Runtime update functionality with user confirmation prompts
  - Multi-region deployment support with `--region` parameter
  - Command-line options: `--skip-build`, `--test-only`, `--help-extended`
  - SSM parameter management for execution roles and runtime ARNs
- **Model Configuration Optimization**: Tuned Claude model settings for infrastructure tasks
  - `MAX_TOKENS = 4096`: Comprehensive analysis and troubleshooting
  - `TOP_P = 0.9`: Balanced creativity while maintaining technical accuracy
  - `Temperature = 0.3`: Consistent, deterministic responses
- **Enhanced MCP Error Handling**: Smart error detection and user-friendly messages
- **Agent2Agent Type System**: Complete type definitions with validation

#### 🐛 Bug Fixes & Agent-Specific Improvements

##### EKS Agent Enhancements
- **MCP Tools Validation Error**: Fixed `ListToolsResult tools Field required` error
  - Enhanced `get_full_tools_list()` to handle different response formats
  - Added proper error handling for empty responses and type checking
- **Memory Initialization**: Fixed `NameError: name 'memory_name' is not defined`
  - Updated memory functions to accept parameters instead of global variables
  - Improved `create_or_get_memory_resource()` and `initialize_memory()` functions
- **Enhanced Configuration**: Updated SSM parameters to use `/app/eksagent/` prefix
- **Improved Tool Management**: Better tool aggregation and dynamic loading

##### Prometheus Agent Enhancements
- **Exit Hang Fix**: Resolved indefinite hanging when users typed 'exit'
  - Added aggressive timeouts (2-5 seconds) for problematic MCP servers
  - Implemented cleanup timeouts with force exit fallback
  - Fixed region initialization issues in `use_manual_gateway()`
- **Resource Cleanup**: Enhanced MCP resource cleanup to prevent leaks
  - Added detailed logging for cleanup steps
  - Implemented graceful termination with multiple fallback methods
  - Added context manager support and signal handling
- **Duplicate Output Fix**: Eliminated duplicate agent responses
  - Changed strands logging level from INFO to WARNING
  - Moved initialization code to prevent duplicate output on import
- **Memory Initialization**: Fixed undefined variable errors in memory setup

#### 🔧 General Improvements
- **Error Message Style**: Standardized reporting across all agents
- **User Experience**: Cleaner and more informative error messages
- **Agent Reliability**: Enhanced error handling ensures agents continue working
- **MCP Response Handling**: Enhanced support for various response formats
- **A2A Import Issues**: Resolved `ModuleNotFoundError: No module named 'a2a'`

### Previous Release (December 2024)

#### 🏗️ Agent2Agent Integration
- Complete type system in `agent2agent/types.py`
- Cross-agent communication with proper type safety
- Enhanced troubleshooting workflows with multi-agent collaboration
- Working A2A integration examples

#### 🔧 MCP Tools Integration
- Fixed MCP tools not loading from configuration
- 52 AWS MCP tools successfully integrated
- Comprehensive logging suppression for clean output

### Foundation Release

#### 🏗️ Core Framework
- Initial implementation of EKS, VPC, Outposts, and Prometheus agents
- Amazon Bedrock AgentCore integration with memory management
- AWS Cognito authentication and SSM parameter store integration
- Multi-model Claude support with optimized settings

#### 🔗 Integration Features
- MCP (Model Context Protocol) integration with 52 AWS tools
- Streamlit web interfaces for all agents
- DuckDuckGo search integration
- Comprehensive test suite and Docker containerization support

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
- [Agent Improvements](docs/AGENT_IMPROVEMENTS.md) - Consolidated agent improvements and technical details
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