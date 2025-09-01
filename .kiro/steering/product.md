# Product Overview

## AWS AgentCore Telco Project

A comprehensive collection of specialized AWS agents built on Amazon Bedrock AgentCore, designed for telecommunications and cloud infrastructure management.

### Core Agents

- **EKS Agent** - Amazon Elastic Kubernetes Service management and troubleshooting
- **VPC Agent** - Virtual Private Cloud networking and connectivity  
- **Outposts Agent** - AWS Outposts hybrid cloud infrastructure
- **Prometheus Agent** - Monitoring and observability with Amazon Managed Prometheus

### Key Features

- **AgentCore Integration** - Built on Amazon Bedrock AgentCore with memory and gateway functionality
- **Standardized Runtime Pattern** - All agents follow consistent runtime deployment architecture
- **Memory Mandatory** - All runtime agents use persistent memory for context retention
- **Optimized Claude Models** - Multiple Claude model options with tuned parameters for infrastructure tasks
- **MCP-Only Architecture** - All AWS operations use MCP tools exclusively (AgentCore Gateway + AWS MCP servers)
- **MCP Protocol** - Model Context Protocol integration with 52+ AWS tools for comprehensive service integration
- **Memory Management** - Persistent context and preference storage using AgentCore Memory
- **Authentication** - AWS Cognito-based secure authentication
- **Web Search** - DuckDuckGo integration for real-time information retrieval
- **Enhanced Error Handling** - Robust error recovery and user-friendly messaging
- **Cross-Agent Communication** - Agent2Agent protocol for collaborative problem solving

### Runtime Architecture

All agents implement a standardized runtime pattern with MCP-only architecture:
- **MCP-Only Operations** - All AWS operations use MCP tools exclusively through AgentCore Gateway and AWS MCP servers
- **No Hardcoded Tools** - Removed all hardcoded boto3 tools for better scalability and maintainability
- **System Prompt Constants** - Each agent uses dedicated system prompt constants (EKS_SYSTEM_PROMPT, PROMETHEUS_SYSTEM_PROMPT, etc.)
- **Initialization Functions** - Standardized component initialization with proper error handling
- **Graceful Degradation** - Robust error recovery ensures agents continue working even with component failures
- **Consistent Architecture** - All four agents (VPC, Outposts, EKS, Prometheus) follow identical patterns

### Model Configuration

All agents are optimized with infrastructure-specific model settings:
- **Temperature: 0.3** - Consistent, deterministic responses for reliable troubleshooting
- **Max Tokens: 4096** - Comprehensive analysis and detailed explanations
- **Top-P: 0.9** - Balanced creativity while maintaining technical accuracy

These settings ensure agents provide reliable, detailed responses for complex AWS infrastructure management tasks.

### Available Models

- **Claude Sonnet 4** - Latest, most capable model for complex scenarios
- **Claude 3.7 Sonnet** - Enhanced reasoning for advanced troubleshooting
- **Claude 3.5 Sonnet v2** - Balanced performance for general use
- **Claude 3.5 Sonnet v1** - Stable version for production environments
- **Claude 3.5 Haiku** - Fast & efficient for quick responses (default)

### Target Users

Telecommunications and cloud infrastructure teams managing AWS services, particularly those working with:
- Kubernetes clusters and container orchestration
- Network architecture and connectivity
- Hybrid cloud deployments
- Monitoring and observability systems

## Project Status

### Current State (September 2025) ✅
- ✅ **Four Specialized Agents**: EKS, VPC, Outposts, and Prometheus agents fully developed
- ✅ **MCP-Only Architecture Completed**: All agents refactored to use identical MCP-only architecture
- ✅ **Architecture Consistency**: Removed all hardcoded boto3 tools across all agents
- ✅ **Runtime Deployment**: Complete `deploy_runtime.py` system with ECR management
- ✅ **AgentCore Integration**: Memory, gateway, and authentication systems
- ✅ **MCP Protocol**: 52+ AWS tools integrated via Model Context Protocol
- ✅ **Agent2Agent Communication**: Cross-agent collaboration protocol
- ✅ **Streamlit Interfaces**: Interactive web interfaces for all agents
- ✅ **Enhanced Error Handling**: Robust error recovery and user-friendly messaging
- ✅ **Documentation**: Comprehensive documentation and steering guides updated