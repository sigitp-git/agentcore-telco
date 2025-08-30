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

# Runtime invocation
python3 invoke_runtime.py interactive
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

## Error Handling & Reliability

### MCP Tools Integration
- **Smart Error Detection** - Identifies common MCP validation errors
- **Clean Error Messages** - User-friendly error reporting instead of technical stack traces
- **Graceful Degradation** - Agents continue working even when MCP tools are unavailable
- **Multiple Fallback Mechanisms** - Robust error recovery for various failure scenarios

### Memory Management
- **AgentCore Memory Integration** - Persistent context and conversation history
- **Automatic Cleanup** - Proper resource cleanup on agent shutdown
- **Error Recovery** - Graceful handling of memory service unavailability

### Best Practices
- Always use try-catch blocks for external service calls
- Provide informative error messages to users
- Implement timeout mechanisms for long-running operations
- Use structured logging for debugging and monitoring