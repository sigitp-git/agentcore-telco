# Agent2Agent Quick Start Guide

## 🚀 Run the Example

```bash
# From project root - use the convenience script
python3 run_a2a_example.py

# Or run directly
python3 agent2agent/examples/a2a_integration_example_full.py
```

## 📁 Directory Structure

```
agent2agent/
├── README.md                    # Main documentation
├── QUICK_START.md              # This file
├── __init__.py                 # Package initialization
├── types.py                    # A2A type definitions and data models
├── docs/                       # Documentation
│   ├── A2A_INTEGRATION_GUIDE.md      # Complete integration guide
│   └── A2A_IMPLEMENTATION_SUMMARY.md # Implementation summary
├── examples/                   # Example scripts and examples
│   ├── explore_a2a.py         # SDK exploration
│   ├── a2a_example.py         # Basic A2A structures example
│   ├── a2a_integration_example.py # Comprehensive integration example
│   └── a2a_integration_example_full.py # Full working example with EKS agent
└── wrappers/                   # A2A wrapper classes
    ├── __init__.py
    └── eks_a2a_wrapper.py      # EKS agent A2A wrapper
```

## 🔧 Usage in Your Code

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

## 🌐 Cross-Agent Communication

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

## 📖 Documentation

- [README.md](README.md) - Main documentation and features
- [Integration Guide](docs/A2A_INTEGRATION_GUIDE.md) - Complete implementation guide
- [Implementation Summary](docs/A2A_IMPLEMENTATION_SUMMARY.md) - What we've built

## 🎯 Key Benefits

✅ **Enhanced Troubleshooting** - Multi-domain context  
✅ **Automated Collaboration** - Seamless agent communication  
✅ **Faster Resolution** - Richer context for problem solving  
✅ **Reduced Silos** - Break down infrastructure domain barriers  
✅ **Scalable Architecture** - Easy to add new agents