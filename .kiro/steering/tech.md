# Technology Stack

## Core Technologies

### Python Ecosystem
- **Python 3.8+** - Primary development language
- **boto3/botocore** - AWS SDK for Python
- **requests** - HTTP client library
- **python-dotenv** - Environment variable management

### AWS Services
- **Amazon Bedrock AgentCore** - Agent runtime and memory management
- **AWS Systems Manager (SSM)** - Parameter store for configuration
- **AWS Cognito** - Authentication and authorization
- **Amazon Bedrock** - Claude model access

### Agent Framework
- **strands-agents** - Core agent framework
- **strands-agents-tools** - Agent tooling extensions
- **bedrock-agentcore** - AgentCore SDK
- **bedrock-agentcore-starter-toolkit** - Development utilities
- **🚀 strands-agents[a2a]** - Multi-agent orchestration with A2A protocol support (planned)

### Additional Libraries
- **ddgs** - DuckDuckGo search integration
- **fastapi/uvicorn** - Web API framework
- **streamlit** - Web UI for demos
- **aws-opentelemetry-distro** - Observability and tracing

## Build System

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.agents.example .env.agents
# Edit .env.agents with actual values
```

### Common Commands

#### Running Individual Agents
```bash
# Navigate to agent directory
cd eks-agentcore/
python3 agent.py

# Interactive model selection
python3 agent.py --select-model

# Comprehensive runtime deployment
python3 deploy_runtime.py

# Deployment with options
python3 deploy_runtime.py --region us-west-2
python3 deploy_runtime.py --skip-build
python3 deploy_runtime.py --test-only

# Runtime invocation
python3 invoke_runtime.py interactive
```

#### Agent Runtime Pattern
All agents follow a standardized runtime architecture with comprehensive deployment:

```bash
# Standardized deployment system across all agents
cd eks-agentcore/
python3 deploy_runtime.py

# Key deployment features:
# - Automated ECR repository management
# - Docker build and push with error handling
# - Runtime update functionality with user confirmation
# - Multi-region deployment support
# - SSM parameter management for execution roles
# - Command-line options for different deployment scenarios

# Key runtime features:
# - Memory mandatory for context retention
# - MCP configuration automatically disabled
# - System prompt constants (e.g., EKS_SYSTEM_PROMPT)
# - Standardized initialization functions
```

#### Testing
```bash
# Run comprehensive test suite
python3 test_agents.py

# Test specific agent functionality
cd eks-agentcore/
python3 -c "import agent; print('✅ Import successful')"
```

#### Streamlit Demos
```bash
cd eks-agentcore/streamlit/
./run_streamlit.sh
# or
streamlit run streamlit_app.py
```

## Configuration Management

### Environment Variables
- Stored in `.env.agents` file (never committed)
- Contains runtime ARNs and gateway IDs for all agents
- Uses placeholder format in `.env.agents.example`

### SSM Parameters
Each agent requires specific SSM parameters:
- `/app/{agent}agent/agentcore/machine_client_id`
- `/app/{agent}agent/agentcore/cognito_auth_scope`
- `/app/{agent}agent/agentcore/cognito_token_url`
- `/app/{agent}agent/agentcore/runtime_arn`

### AWS Configuration
- Default region: `us-east-1`
- Requires appropriate IAM permissions for each agent's AWS services
- Uses AWS CLI configuration or environment variables

## Agent Runtime Architecture

### Standardized Runtime Pattern
All agents follow a consistent runtime deployment pattern:

```python
# Runtime configuration (in agent_runtime.py)
# Configure MCP settings before importing agent components
from agent import AgentConfig

# Disable MCP configuration for runtime environment
AgentConfig.ENABLE_MCP_CONFIG = False
AgentConfig.ENABLE_AWS_MCP = False

# Import agent module and initialization functions
import agent
from agent import create_agent_hooks, create_tools_list, AgentConfig

def create_runtime_agent():
    """Create the runtime agent with memory and tools."""
    # Initialize runtime components
    model, memory_id, memory_client, mcp_client = agent.initialize_runtime_components()
    
    # Create agent with system prompt constant
    runtime_agent = Agent(
        model=model,
        tools=tools,
        hooks=hooks,
        system_prompt=AgentConfig.AGENT_SYSTEM_PROMPT  # Agent-specific constant
    )
    return runtime_agent
```

### Runtime Features
- **Memory Mandatory**: All runtime agents use persistent memory
- **MCP Configuration Disabled**: Prevents initialization conflicts
- **System Prompt Constants**: Agent-specific prompts (EKS_SYSTEM_PROMPT, etc.)
- **Initialization Functions**: Standardized component setup
- **Error Handling**: Robust error recovery with graceful degradation

## Model Configuration

### Claude Model Settings
All agents are configured with optimized model parameters:

```python
# Model Settings (in AgentConfig class)
MODEL_TEMPERATURE = 0.3  # Deterministic responses for consistent troubleshooting
MAX_TOKENS = 4096        # Sufficient for detailed analysis and comprehensive responses  
TOP_P = 0.9              # Balanced creativity for problem-solving while maintaining technical accuracy
```

### Available Models
- **Claude Sonnet 4** - Latest, most capable model
- **Claude 3.7 Sonnet** - Enhanced reasoning capabilities
- **Claude 3.5 Sonnet v2** - Balanced performance (recommended)
- **Claude 3.5 Sonnet v1** - Stable version
- **Claude 3.5 Haiku** - Fast & efficient (default for development)

### Model Selection
```bash
# Interactive model selection
python3 agent.py --select-model

# Programmatic model selection
from agent import AgentConfig
AgentConfig.set_model('claude-3-5-sonnet-v2')
```

## Development Status

### Completed Components (September 2025) ✅
- ✅ **MCP-Only Architecture**: All four agents refactored to use identical MCP-only architecture
- ✅ **Architecture Consistency**: Removed hardcoded boto3 tools, unified tool discovery patterns
- ✅ **Agent Development**: All four agents (EKS, VPC, Outposts, Prometheus) fully implemented
- ✅ **Runtime System**: Complete deployment and management infrastructure
- ✅ **MCP Integration**: Model Context Protocol with 52+ AWS tools
- ✅ **Memory System**: Persistent context and conversation history
- ✅ **Authentication**: AWS Cognito integration
- ✅ **Error Handling**: Enhanced error recovery and user messaging
- ✅ **Agent2Agent**: Cross-agent communication protocol
- ✅ **A2A Strands Framework Planning**: Complete implementation roadmap for multi-agent orchestration

### Planned Components (Q1 2026) 🚀
- 🚀 **A2A Protocol Integration**: Agent-to-Agent protocol for cross-platform communication
- 🚀 **Multi-Agent Orchestration**: Swarm, Graph, and Workflow patterns for collaborative problem-solving
- 🚀 **Auto-Discovery Service**: Centralized agent registration and capability mapping
- 🚀 **Cross-Agent Tool Integration**: Seamless tool sharing between specialized agents
- 🚀 **Intelligent Agent Selection**: Automatic routing based on query analysis and agent capabilities
- 🚀 **Collaborative Workflows**: Complex infrastructure problems solved by agent teams

## MCP-Only Architecture (September 2025)

### Architecture Transformation
All agents have been refactored to use MCP-only architecture:

**Before (Mixed Architecture):**
- Hardcoded boto3 tools for direct AWS API calls
- Static guidance tools with hardcoded information
- Mixed MCP and direct SDK usage

**After (Pure MCP Architecture):**
- **AgentCore Gateway MCP Tools**: For advanced integrations and cross-service operations
- **AWS MCP Servers**: For all AWS service operations (EKS, CloudWatch, EC2, VPC, etc.)
- **Websearch**: For real-time documentation and information
- **MCP Management Tools**: For configuration, discovery, and troubleshooting

### Consistency Across All Agents
All four agents (VPC, Outposts, EKS, Prometheus) now have:
- ✅ **Identical MCP-only architecture**
- ✅ **Consistent configuration logic**
- ✅ **Unified tool discovery and help systems**
- ✅ **Clean user-facing interfaces**
- ✅ **Specialized system prompts for their respective domains**
- ✅ **Enhanced error handling with user-friendly messages**

## A2A Strands Multi-Agent Orchestration Framework (Planned Q1 2026) 🚀

### Framework Architecture
The A2A Strands framework will enable intelligent collaboration between the four specialized agents:

#### Core Components
- **Auto-Discovery Service**: Centralized agent registration and capability mapping
- **A2A Protocol Integration**: Cross-platform agent communication using Agent-to-Agent protocol
- **Intelligent Agent Selection**: Automatic routing based on query analysis and agent capabilities
- **Cross-Agent Tool Integration**: Seamless tool sharing between specialized agents

#### Orchestration Patterns
```python
# Agents as Tools Pattern - Hierarchical delegation
@tool
def eks_cluster_analysis(cluster_name: str, issue_description: str) -> str:
    """Analyze EKS cluster issues using the specialized EKS agent."""
    # Implementation calls EKS agent via A2A protocol

# Swarm Pattern - Collaborative problem-solving
from strands.multiagent import Swarm
swarm = Swarm([eks_agent_proxy, vpc_agent_proxy, prometheus_agent_proxy])
result = swarm("Diagnose complex infrastructure issue")

# Graph Pattern - Deterministic workflows
from strands.multiagent import GraphBuilder
builder = GraphBuilder()
builder.add_node(prometheus_agent_proxy, "monitoring_check")
builder.add_node(vpc_agent_proxy, "network_analysis")
builder.add_edge("monitoring_check", "network_analysis")
```

#### Implementation Phases (6 weeks)
1. **Phase 1**: A2A Protocol Integration - Each agent exposes itself as an A2A server
2. **Phase 2**: Agent Discovery and Registration - Centralized discovery service
3. **Phase 3**: Cross-Agent Tool Integration - Agents can invoke each other's tools
4. **Phase 4**: Collaborative Workflows - Swarm and Graph patterns
5. **Phase 5**: Enhanced System Prompts - Agents become collaboration-aware

#### Deployment Architecture
```yaml
# Container orchestration for multi-agent deployment
services:
  eks-agent:
    ports: ["9001:9001"]
    environment: [AGENT_TYPE=eks, A2A_PORT=9001]
  vpc-agent:
    ports: ["9002:9002"] 
    environment: [AGENT_TYPE=vpc, A2A_PORT=9002]
  # ... other agents
  discovery-service:
    ports: ["9000:9000"]
```

### Technical Benefits
- **Intelligent Problem-Solving**: EKS networking issues automatically involve VPC and Prometheus agents
- **Unified User Experience**: Comprehensive solutions regardless of which agent users start with
- **Collaborative Workflows**: Complex infrastructure problems solved by specialized agent teams
- **Auto-Discovery**: Agents automatically find and utilize peer agent capabilities

## Error Handling & Reliability

### MCP Tools Integration
- **Smart Error Detection** - Identifies common MCP validation errors
- **Clean Error Messages** - User-friendly error reporting instead of technical stack traces
- **Graceful Degradation** - Agents continue working even when MCP tools are unavailable
- **Multiple Fallback Mechanisms** - Robust error recovery for various failure scenarios
- **MCP-Only Operations** - All AWS operations use MCP tools exclusively

### Memory Management
- **AgentCore Memory Integration** - Persistent context and conversation history
- **Automatic Cleanup** - Proper resource cleanup on agent shutdown
- **Error Recovery** - Graceful handling of memory service unavailability

### Multi-Agent Error Handling (Planned) 🚀
- **Cross-Agent Timeout Management** - Prevent runaway multi-agent processes
- **Agent Failure Recovery** - Graceful degradation when peer agents are unavailable
- **Circular Dependency Prevention** - Avoid infinite agent delegation loops
- **Resource Exhaustion Protection** - Rate limiting and timeout controls for agent interactions

### Best Practices
- Always use try-catch blocks for external service calls
- Provide informative error messages to users
- Implement timeout mechanisms for long-running operations
- Use structured logging for debugging and monitoring
- All AWS operations must use MCP tools exclusively
- **🚀 Multi-Agent Coordination**: Design agents for collaboration and delegation when implementing A2A Strands
- **🚀 Capability-Based Routing**: Use agent capabilities for intelligent task delegation
- **🚀 Shared Context Management**: Maintain context across multi-agent workflows
- **🚀 Agent Discovery Patterns**: Implement robust discovery and registration mechanisms
- **🚀 Cross-Agent Security**: Secure A2A communication and authentication between agents