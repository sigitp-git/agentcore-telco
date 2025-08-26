# A2A Integration Guide for AWS Telco Agents

This guide shows how to integrate the Agent2Agent (A2A) protocol into your existing AWS AgentCore telco agents.

## Overview

The A2A protocol enables your EKS, VPC, Outposts, and Prometheus agents to:
- **Discover each other's capabilities** automatically
- **Collaborate on complex tasks** that span multiple domains
- **Share context and insights** for enhanced troubleshooting
- **Maintain security** without exposing internal state

## Installation

The A2A SDK is already installed in your project:

```bash
# Already done via uv add a2a-sdk
uv add a2a-sdk
```

## Key A2A Components

### 1. Agent Cards
Define what your agent can do and how to reach it:

```python
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, AgentProvider

eks_card = AgentCard(
    name="EKS-Agent",
    version="1.0.0",
    description="AWS EKS management and troubleshooting agent",
    url="https://eks-agent.internal:8001",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False,
        state_transition_history=True
    ),
    skills=[
        AgentSkill(
            id="cluster-mgmt",
            name="cluster_management",
            description="Manage EKS clusters",
            tags=["kubernetes", "eks", "cluster"]
        )
    ],
    provider=AgentProvider(
        organization="AWS Telco Team",
        url="https://aws.amazon.com"
    ),
    default_input_modes=["text"],
    default_output_modes=["text", "json"]
)
```

### 2. Messages
Structure communication between agents:

```python
from a2a.types import Message, TextPart, Role

request = Message(
    message_id="req-001",
    role=Role.user,
    parts=[TextPart(text="Analyze network connectivity for pod web-app-123")],
    kind="message"
)
```

### 3. Client Communication
Send requests to other agents:

```python
from a2a.client import ClientFactory

# Create client for target agent
client = ClientFactory.create_client("https://vpc-agent.internal:8002")

# Send message
response = await client.send_message(request)
```

## Integration Steps

### Step 1: Add A2A Wrapper to Existing Agents

Create `a2a_wrapper.py` in each agent directory:

```python
#!/usr/bin/env python3
"""
A2A wrapper for existing AgentCore agents
"""

import asyncio
import json
from typing import Dict, Optional
from a2a.client import ClientFactory
from a2a.types import AgentCard, Message, TextPart, Role

class A2AAgentWrapper:
    """Makes existing AgentCore agents A2A-compatible"""
    
    def __init__(self, agent_instance, agent_card: AgentCard):
        self.agent = agent_instance
        self.agent_card = agent_card
        self.clients: Dict[str, object] = {}
    
    async def get_client(self, target_url: str):
        """Get or create A2A client for target agent"""
        if target_url not in self.clients:
            self.clients[target_url] = ClientFactory.create_client(target_url)
        return self.clients[target_url]
    
    async def send_request(self, target_url: str, request_text: str) -> Optional[str]:
        """Send A2A request to another agent"""
        try:
            client = await self.get_client(target_url)
            
            message = Message(
                message_id=f"req-{hash(request_text)}",
                role=Role.user,
                parts=[TextPart(text=request_text)],
                kind="message"
            )
            
            response = await client.send_message(message)
            
            if response and response.parts:
                return response.parts[0].text
            
        except Exception as e:
            print(f"A2A request failed: {e}")
            return None
    
    async def handle_request(self, message: Message) -> Message:
        """Handle incoming A2A requests"""
        # Parse request and route to appropriate agent method
        request_text = message.parts[0].text if message.parts else ""
        
        # Route based on request content
        response_text = await self._route_request(request_text)
        
        return Message(
            message_id=f"resp-{message.message_id}",
            role=Role.agent,
            parts=[TextPart(text=response_text)],
            kind="message"
        )
    
    async def _route_request(self, request: str) -> str:
        """Route request to appropriate agent method"""
        # Implement routing logic based on your agent's capabilities
        return f"Processed request: {request}"
```

### Step 2: Modify Existing Agent Classes

Add A2A integration to your existing agents. For example, in `eks-agentcore/agent.py`:

```python
# Add to imports
from a2a_wrapper import A2AAgentWrapper
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, AgentProvider

class EKSAgent:
    def __init__(self):
        # Existing initialization...
        
        # A2A Integration
        self.a2a_wrapper = None
        self._setup_a2a_integration()
    
    def _setup_a2a_integration(self):
        """Setup A2A integration"""
        agent_card = AgentCard(
            name="EKS-Agent",
            version="1.0.0",
            description="AWS EKS management and troubleshooting agent",
            url="https://eks-agent.internal:8001",
            capabilities=AgentCapabilities(
                streaming=True,
                push_notifications=False,
                state_transition_history=True
            ),
            skills=[
                AgentSkill(
                    id="cluster-mgmt",
                    name="cluster_management", 
                    description="Manage EKS clusters",
                    tags=["kubernetes", "eks", "cluster"]
                ),
                AgentSkill(
                    id="pod-diagnostics",
                    name="pod_diagnostics",
                    description="Diagnose pod issues",
                    tags=["kubernetes", "pods", "diagnostics"]
                )
            ],
            provider=AgentProvider(
                organization="AWS Telco Team",
                url="https://aws.amazon.com"
            ),
            default_input_modes=["text"],
            default_output_modes=["text", "json"]
        )
        
        self.a2a_wrapper = A2AAgentWrapper(self, agent_card)
    
    async def request_vpc_analysis(self, vpc_id: str, issue_description: str) -> Optional[str]:
        """Request VPC analysis from VPC Agent via A2A"""
        if not self.a2a_wrapper:
            return None
        
        request = f"analyze_network_connectivity vpc_id={vpc_id} issue={issue_description}"
        vpc_agent_url = "https://vpc-agent.internal:8002"
        
        return await self.a2a_wrapper.send_request(vpc_agent_url, request)
    
    async def request_metrics_context(self, cluster_name: str, timeframe: str) -> Optional[str]:
        """Request metrics from Prometheus Agent via A2A"""
        if not self.a2a_wrapper:
            return None
        
        request = f"get_cluster_metrics cluster={cluster_name} timeframe={timeframe}"
        prometheus_agent_url = "https://prometheus-agent.internal:8003"
        
        return await self.a2a_wrapper.send_request(prometheus_agent_url, request)
```

### Step 3: Add A2A Server Endpoints

Create `a2a_server.py` for each agent:

```python
#!/usr/bin/env python3
"""
A2A server endpoint for agent
"""

from fastapi import FastAPI
from a2a.types import Message
from agent import EKSAgent  # Import your actual agent
from a2a_wrapper import A2AAgentWrapper

app = FastAPI()
agent = EKSAgent()

@app.post("/a2a/message")
async def handle_a2a_message(message: Message) -> Message:
    """Handle incoming A2A messages"""
    return await agent.a2a_wrapper.handle_request(message)

@app.get("/a2a/card")
async def get_agent_card():
    """Return agent card for discovery"""
    return agent.a2a_wrapper.agent_card

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Step 4: Agent Discovery Service

Create `a2a_discovery.py` for agent registry:

```python
#!/usr/bin/env python3
"""
A2A Agent Discovery Service
"""

import asyncio
from typing import Dict, List
from a2a.types import AgentCard

class A2ADiscoveryService:
    """Service for discovering available A2A agents"""
    
    def __init__(self):
        self.agents: Dict[str, str] = {
            "EKS-Agent": "https://eks-agent.internal:8001",
            "VPC-Agent": "https://vpc-agent.internal:8002", 
            "Outposts-Agent": "https://outposts-agent.internal:8003",
            "Prometheus-Agent": "https://prometheus-agent.internal:8004"
        }
    
    async def discover_agents(self) -> List[AgentCard]:
        """Discover all available agents"""
        agent_cards = []
        
        for agent_name, agent_url in self.agents.items():
            try:
                # In real implementation, fetch agent card from each agent
                # card = await fetch_agent_card(agent_url)
                # agent_cards.append(card)
                pass
            except Exception as e:
                print(f"Failed to discover {agent_name}: {e}")
        
        return agent_cards
    
    def get_agent_url(self, agent_name: str) -> str:
        """Get URL for specific agent"""
        return self.agents.get(agent_name)
```

## Usage Examples

### Cross-Agent Troubleshooting

```python
# EKS Agent detects pod connectivity issues
pod_issues = await eks_agent.diagnose_pod("web-app-123", "production")

if pod_issues.get("network_related"):
    # Request VPC analysis
    vpc_analysis = await eks_agent.request_vpc_analysis(
        vpc_id="vpc-prod-123",
        issue_description="Pod connectivity failure"
    )
    
    # Request metrics context
    metrics = await eks_agent.request_metrics_context(
        cluster_name="prod-cluster",
        timeframe="last_1h"
    )
    
    # Combine insights for comprehensive troubleshooting
    combined_analysis = {
        "pod_diagnosis": pod_issues,
        "vpc_analysis": vpc_analysis,
        "metrics_context": metrics
    }
```

### Monitoring Integration

```python
# Any agent can request monitoring context
async def enhanced_diagnostics(self, resource_id: str):
    """Enhanced diagnostics with monitoring context"""
    
    # Get metrics from Prometheus Agent
    metrics = await self.a2a_wrapper.send_request(
        "https://prometheus-agent.internal:8004",
        f"get_resource_metrics resource_id={resource_id} timeframe=1h"
    )
    
    # Perform local analysis with metrics context
    local_analysis = await self.analyze_resource(resource_id)
    
    return {
        "local_analysis": local_analysis,
        "metrics_context": metrics,
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Deployment Considerations

### 1. Network Configuration
- Ensure agents can reach each other on configured ports
- Use internal DNS or service discovery for agent URLs
- Consider load balancing for high availability

### 2. Security
- Implement authentication between agents
- Use TLS for encrypted communication
- Validate agent certificates

### 3. Monitoring
- Monitor A2A communication health
- Track cross-agent request latency
- Alert on agent discovery failures

## Benefits

1. **Enhanced Troubleshooting**: Agents can collaborate for comprehensive analysis
2. **Reduced Silos**: Break down barriers between different infrastructure domains
3. **Context Sharing**: Agents provide richer context to each other
4. **Scalability**: Easy to add new agents to the ecosystem
5. **Flexibility**: Agents remain independent while gaining collaboration capabilities

## Next Steps

1. Implement A2A wrappers for each agent
2. Set up agent discovery service
3. Deploy A2A server endpoints
4. Test cross-agent communication
5. Monitor and optimize performance

This integration transforms your individual telco agents into a collaborative ecosystem, enabling more powerful and comprehensive infrastructure management capabilities.