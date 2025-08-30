# Project Structure

## Directory Organization

```
agentcore-telco/
├── .env.agents.example          # Environment template (safe to commit)
├── .env.agents                  # Actual environment (never commit)
├── .gitignore                   # Comprehensive ignore rules
├── README.md                    # Main project documentation
├── LICENSE                      # MIT License for the entire project
├── test_agents.py               # Comprehensive test suite
├── docs/                        # Documentation
│   ├── AGENT_IMPROVEMENTS.md    # Consolidated agent improvements and technical details
│   ├── DOCUMENTATION_CONSOLIDATION_SUMMARY.md # Documentation consolidation summary
│   └── telco-architecture-pattern.md # Telco architecture patterns
├── eks-agentcore/               # EKS Agent
├── vpc-agentcore/               # VPC Agent  
├── outposts-agentcore/          # Outposts Agent
├── prometheus-agentcore/        # Prometheus Agent
└── __pycache__/                 # Python cache (ignored)
```

## Agent Directory Structure

Each agent follows the same standardized structure:

```
{agent}-agentcore/
├── agent.py                     # Main agent implementation
├── agent_runtime.py             # Runtime configuration
├── deploy_runtime.py            # Deployment utilities
├── invoke_runtime.py            # Runtime invocation interface
├── select_model.py              # Model selection utility
├── utils.py                     # Shared utility functions
├── requirements.txt             # Agent-specific dependencies
├── activate_env.sh              # Environment activation script
├── run_streamlit.sh             # Streamlit launcher
├── Dockerfile.runtime           # Container configuration
├── streamlit/                   # Streamlit demo application
│   ├── demo_streamlit.py
│   ├── run_streamlit.sh
│   └── streamlit_app.py
└── __pycache__/                 # Python cache (ignored)
```

## Key File Patterns

### Core Agent Files
- **agent.py** - Main agent logic, tools, memory management, MCP integration
- **invoke_runtime.py** - AgentRuntimeInvoker class for programmatic access
- **utils.py** - Shared utilities (SSM, AWS helpers, config loading)
- **requirements.txt** - Python dependencies (consistent across agents)

### Configuration Files
- **.env.agents** - Runtime ARNs and gateway IDs (never committed)
- **SSM Parameters** - Stored in AWS Systems Manager Parameter Store
- **Dockerfile.runtime** - Container deployment configuration

### Testing and Demos
- **test_agents.py** - Root-level comprehensive test suite
- **streamlit/** - Web UI demos for each agent
- **activate_env.sh** - Environment setup scripts

## Naming Conventions

### Directories
- Agent directories: `{service}-agentcore/` (e.g., `eks-agentcore/`)
- Lowercase with hyphens for multi-word services

### Files
- Python files: `snake_case.py`
- Shell scripts: `snake_case.sh`
- Configuration: `.env.agents`, `requirements.txt`

### Environment Variables
- Format: `{AGENT}_AGENT_{TYPE}` (e.g., `EKS_AGENT_RUNTIME_ARN`)
- All uppercase with underscores

### SSM Parameters
- Format: `/app/{agent}agent/agentcore/{parameter}`
- Example: `/app/eksagent/agentcore/machine_client_id`

## Code Organization Patterns

### Agent Class Structure
```python
class AgentConfig:
    # Configuration constants
    DEFAULT_REGION = 'us-east-1'
    AVAILABLE_MODELS = {...}
    
    # Model Settings (optimized for infrastructure tasks)
    MODEL_TEMPERATURE = 0.3  # Deterministic responses
    MAX_TOKENS = 4096        # Comprehensive analysis
    TOP_P = 0.9              # Balanced creativity
    
class MemoryManager:
    # Memory lifecycle management
    
class {Agent}MemoryHooks(HookProvider):
    # Memory hooks for context retrieval
    
class AWSMCPManager:
    # AWS MCP tools integration with enhanced error handling
```

### Tool Definitions
```python
@tool
def tool_name(param: type) -> str:
    """Tool description."""
    # Implementation
```

### Model Initialization
```python
# Create model with optimized settings
model = BedrockModel(
    model_id=model_id,
    temperature=AgentConfig.MODEL_TEMPERATURE,
    max_tokens=AgentConfig.MAX_TOKENS,
    top_p=AgentConfig.TOP_P
)
```

### Error Handling Patterns
```python
# MCP tools error handling
try:
    tools = client.list_tools_sync()
    # Handle different response formats
    if isinstance(tools, dict):
        return tools.get('tools', [])
    elif isinstance(tools, list):
        return tools
    return []
except Exception as e:
    # Provide clean error messages
    error_str = str(e).lower()
    if "validation error" in error_str and "tools" in error_str:
        print("ℹ️  No MCP tools available")
    else:
        print("ℹ️  MCP tools unavailable")
    return []
```

### Import Organization
1. Standard library imports
2. Third-party imports (boto3, requests, etc.)
3. Agent framework imports (strands, bedrock-agentcore)
4. Local imports (utils, config)

## Documentation

### Primary Documentation (docs/)
- **README.md**: Main project documentation with comprehensive guide
- **docs/AGENT_IMPROVEMENTS.md**: Technical details and improvements for all agents
- **docs/DOCUMENTATION_CONSOLIDATION_SUMMARY.md**: Documentation consolidation summary
- **docs/telco-architecture-pattern.md**: Telco architecture patterns

### Specialized Documentation (Preserved)
- **MCP Integration Docs**: awslabs-mcp-lambda/mcp/ directory
- **A2A Protocol Docs**: agent2agent/ directory
- **Agent-Specific Docs**: Individual agent directories for runtime-specific documentation

### Documentation Principles
- **Consolidated Structure**: All general documentation in docs/ directory
- **No Duplicate Information**: All content consolidated without information loss
- **Clear Hierarchy**: Primary docs → Specialized docs → Technical details

## Security Considerations

### Never Commit
- `.env.agents` - Contains actual ARNs and IDs
- AWS credentials or keys
- SSM parameter values
- Any files with real account IDs or sensitive data

### Always Use Placeholders
- In documentation and examples
- In `.env.agents.example`
- Format: `ACCOUNT_ID`, `REGION`, `RUNTIME_ID`, `GATEWAY_ID`