# Agent2Agent Integration

This directory contains the Agent2Agent protocol integration for AWS Telco AgentCore agents.

## Directory Structure

```
agent2agent/
├── README.md                    # This file
├── __init__.py                  # Package initialization
├── types.py                     # A2A type definitions and data models
├── docs/                        # Documentation
│   ├── A2A_INTEGRATION_GUIDE.md      # Complete integration guide
│   └── A2A_IMPLEMENTATION_SUMMARY.md # Implementation summary
├── examples/                    # Example scripts and examples
│   ├── __init__.py
│   ├── explore_a2a.py          # SDK exploration
│   ├── a2a_example.py          # Basic A2A structures example
│   ├── a2a_integration_example.py # Comprehensive integration example
│   └── a2a_integration_example_full.py # Full working example with EKS agent
└── wrappers/                    # A2A wrapper classes
    ├── __init__.py
    └── eks_a2a_wrapper.py       # EKS agent A2A wrapper
```

## Quick Start

### 1. Run the Example

```bash
# From project root
python3 agent2agent/examples/a2a_integration_example_full.py
# Or use the convenience script
python3 run_a2a_example.py
```

### 2. Use A2A Types and Wrapper in Your Agent

```python
# Import A2A types for protocol communication
from agent2agent.types import (
    AgentCard, AgentCapabilities, AgentSkill, AgentProvider,
    Message, TextPart, Role, A2ARequest, A2AResponse
)

# Import the EKS A2A wrapper
from agent2agent.wrappers.eks_a2a_wrapper import EKSA2AWrapper

# In your EKS agent
eks_agent = YourEKSAgent()
a2a_wrapper = EKSA2AWrapper(eks_agent)

# Enhanced troubleshooting with cross-agent collaboration
result = await a2a_wrapper.enhanced_pod_troubleshooting(
    pod_name="web-app-123",
    namespace="production",
    cluster_name="prod-cluster"
)
```

### 3. Cross-Agent Communication

```python
# Request VPC analysis
vpc_response = await a2a_wrapper.send_request_to_agent("VPC-Agent", {
    "action": "analyze_network_connectivity",
    "vpc_id": "vpc-prod-123",
    "issue_description": "Pod connectivity issues"
})

# Request metrics from Prometheus
metrics = await a2a_wrapper.send_request_to_agent("Prometheus-Agent", {
    "action": "get_cluster_metrics", 
    "cluster_name": "prod-cluster",
    "timeframe": "1h"
})
```

## Key Features

- **Complete Type System**: Full A2A protocol type definitions with validation
- **Agent Discovery**: Automatic discovery of available agents and their capabilities
- **Cross-Agent Communication**: Seamless request/response between agents
- **Enhanced Troubleshooting**: Multi-domain context for comprehensive analysis
- **Collaborative Workflows**: Agents work together on complex infrastructure issues
- **Comprehensive Recommendations**: Combined insights from multiple agents
- **Structured Messaging**: Type-safe message passing with role-based communication

## A2A Type System

The `agent2agent.types` module provides comprehensive type definitions for the Agent2Agent protocol:

### Core Types

```python
from agent2agent.types import (
    # Message types
    Message, TextPart, Role,
    
    # Agent metadata
    AgentCard, AgentCapabilities, AgentSkill, AgentProvider,
    
    # Request/Response
    A2ARequest, A2AResponse,
    
    # Utility functions
    create_text_message, create_agent_skill, create_basic_capabilities
)
```

### Agent Card Example

```python
from agent2agent.types import AgentCard, AgentCapabilities, AgentSkill, AgentProvider

# Create agent capabilities
capabilities = AgentCapabilities(
    streaming=True,
    push_notifications=False,
    state_transition_history=True
)

# Define agent skills
skills = [
    AgentSkill(
        id="eks-cluster-management",
        name="cluster_management",
        description="Create, update, delete, and troubleshoot EKS clusters",
        tags=["kubernetes", "eks", "cluster"]
    )
]

# Create agent card
agent_card = AgentCard(
    name="EKS-Agent",
    version="1.0.0",
    description="AWS EKS management and troubleshooting agent",
    url="https://eks-agent.internal:8001",
    capabilities=capabilities,
    skills=skills,
    provider=AgentProvider(organization="AWS Telco Team"),
    default_input_modes=["text", "json"],
    default_output_modes=["text", "json", "yaml"]
)
```

### Message Communication

```python
from agent2agent.types import Message, TextPart, Role, create_text_message

# Create a simple message
message = create_text_message(
    text="Analyze pod connectivity issues",
    role=Role.user,
    context_id="troubleshooting-session-123"
)

# Create a complex message
complex_message = Message(
    message_id="req-12345",
    role=Role.agent,
    parts=[
        TextPart(text="Pod analysis complete"),
        TextPart(text="Recommendations: Scale cluster, check DNS")
    ],
    context_id="troubleshooting-session-123"
)
```

## Documentation

- [Integration Guide](docs/A2A_INTEGRATION_GUIDE.md) - Complete implementation guide
- [Implementation Summary](docs/A2A_IMPLEMENTATION_SUMMARY.md) - What we've built

## Examples

- [Basic Example](examples/a2a_example.py) - Explore A2A data structures
- [Integration Example](examples/a2a_integration_example.py) - Comprehensive example
- [Full Example](examples/a2a_integration_example_full.py) - Complete example with EKS agent

## Next Steps

1. **Deploy A2A Servers** - Set up FastAPI endpoints for each agent
2. **Implement Real Clients** - Replace simulated responses with actual A2A clients
3. **Add Authentication** - Secure agent-to-agent communication
4. **Service Discovery** - Dynamic agent discovery and registration
5. **Monitoring** - Track A2A communication health and performance

## Benefits

✅ **Enhanced Troubleshooting** - Multi-domain context for comprehensive analysis  
✅ **Automated Collaboration** - Seamless communication between agents  
✅ **Faster Resolution** - Richer context leads to quicker problem solving  
✅ **Reduced Silos** - Break down barriers between infrastructure domains  
✅ **Scalable Architecture** - Easy to add new agents to the ecosystem