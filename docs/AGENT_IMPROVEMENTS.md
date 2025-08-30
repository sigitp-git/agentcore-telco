# Agent Improvements & Technical Details

This document consolidates all agent-specific improvements, fixes, and technical details for the AWS AgentCore Telco project.

## Latest Runtime Pattern (August 2025)

### Standardized Agent Runtime Architecture & Deployment

All agents now follow a consistent runtime pattern for AgentCore deployment with comprehensive deployment automation:

#### Key Runtime Features
- **Comprehensive Deployment System**: Standardized `deploy_runtime.py` across all agents with:
  - Automated ECR repository management (creates when needed)
  - Docker build and push with comprehensive error handling
  - Runtime update functionality with user confirmation prompts
  - Multi-region deployment support with `--region` parameter
  - Command-line options: `--skip-build`, `--test-only`, `--help-extended`
  - SSM parameter management for execution roles and runtime ARNs
- **Memory Mandatory**: All runtime agents use persistent memory for context retention
- **MCP Configuration Disabled**: Runtime environment automatically disables MCP configuration to prevent initialization conflicts
- **System Prompt Constants**: Each agent uses a dedicated system prompt constant stored in `AgentConfig`
- **Initialization Functions**: Standardized component initialization with proper error handling
- **Enhanced Error Handling**: Robust error recovery with graceful degradation

#### Runtime Configuration Pattern
```python
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

#### Standardized Deployment System

All agents now include a comprehensive `deploy_runtime.py` script with:

**Core Deployment Features:**
- **ECR Repository Management**: Automatically creates ECR repositories when needed
- **Docker Build & Push**: Handles containerization with comprehensive error handling
- **Runtime Updates**: Updates existing runtimes with user confirmation prompts
- **Multi-Region Support**: Deploy to any AWS region with `--region` parameter
- **SSM Integration**: Manages execution roles and runtime ARNs in Parameter Store

**Command-Line Options:**
```bash
python3 deploy_runtime.py                    # Standard deployment
python3 deploy_runtime.py --region us-west-2 # Deploy to specific region
python3 deploy_runtime.py --skip-build       # Skip Docker build step
python3 deploy_runtime.py --test-only        # Test deployment without changes
python3 deploy_runtime.py --help-extended    # Show detailed help
```

**Deployment Status (August 2025):**
- ✅ **EKS Agent**: Successfully deployed with new ECR repository
- ✅ **VPC Agent**: Successfully deployed with new ECR repository  
- ✅ **Outposts Agent**: Existing runtime ready (deployment available)
- ✅ **Prometheus Agent**: Successfully deployed with existing ECR repository

#### Standardized Initialization Functions

All agents now include these standardized functions:

1. **`initialize_runtime_components()`** - Main initialization function
2. **`setup_gateway_and_mcp()`** - Gateway and MCP client setup
3. **`setup_memory()`** - Memory client initialization

#### System Prompt Constants

Each agent has a dedicated system prompt constant:
- **EKS Agent**: `AgentConfig.EKS_SYSTEM_PROMPT`
- **VPC Agent**: `AgentConfig.VPC_SYSTEM_PROMPT`
- **Outposts Agent**: `AgentConfig.OUTPOSTS_SYSTEM_PROMPT`
- **Prometheus Agent**: `AgentConfig.PROMETHEUS_SYSTEM_PROMPT`

## EKS Agent Improvements

### Overview
The EKS agent has been successfully upgraded with the latest runtime pattern and enhanced functionality for better MCP integration, resource management, and error handling.

### Key Improvements Added

#### 1. Model Configuration Optimization
- **MAX_TOKENS**: Set to 4096 for comprehensive EKS analysis and troubleshooting
- **TOP_P**: Set to 0.9 for balanced creativity while maintaining technical accuracy
- **Temperature**: Maintained at 0.3 for consistent, deterministic responses
- **Infrastructure-Tuned**: Settings specifically optimized for AWS infrastructure tasks

#### 2. Enhanced MCP Error Handling
- **Smart Error Detection**: Identifies common MCP validation errors and provides clean messages
- **User-Friendly Messages**: Replaces technical stack traces with informative status messages
- **Graceful Degradation**: Agent continues working even when MCP tools are unavailable
- **Multiple Fallback Mechanisms**: Robust error recovery for various failure scenarios

#### 3. AWSMCPManager Class
- **Purpose**: Manages AWS MCP tools integration with timeout handling
- **Features**:
  - Automatic initialization of AWS MCP servers from configuration
  - Timeout handling for problematic servers
  - Proper cleanup of stdio processes
  - Context manager support for resource management
  - Enhanced error handling with clean user messages

#### 4. Enhanced Configuration System
- **MCP Configuration**: Added toggles and paths for MCP config loading
- **AWS MCP Integration**: Separate configuration for AWS MCP tools
- **Improved Region Setup**: Better AWS region configuration with validation
- **Configuration Methods**: Added methods for loading and managing MCP server configs

#### 5. Proper Resource Cleanup
- **Cleanup Functions**: Added `cleanup_all_resources()` and `emergency_cleanup()`
- **Signal Handlers**: Proper handling of SIGINT and SIGTERM for graceful shutdown
- **Timeout Management**: Prevents hanging during cleanup operations
- **Emergency Exit**: Force exit mechanisms to prevent process hanging

#### 6. Improved Initialization Architecture
- **Deferred Initialization**: All components now initialized in main() function
- **Global Variables**: Proper management of global state variables
- **Error Handling**: Better error handling during initialization
- **Component Dependencies**: Proper ordering of component initialization

#### 7. Enhanced Command Line Interface
- **Structured Arguments**: Moved command line handling to separate function
- **Help System**: Enhanced help with MCP configuration information
- **Model Selection**: Improved interactive model selection

#### 8. Memory System Updates
- **EKS-Specific Naming**: Updated memory names and namespaces for EKS context
- **Proper Hooks**: Updated memory hooks to use EKS-specific naming
- **SSM Parameters**: Updated to use `/app/eksagent/` prefix instead of `/app/devopsagent/`

### EKS Agent Fixes Applied

#### 1. MCP Tools Validation Error
**Error**: `1 validation error for ListToolsResult tools Field required [type=missing, input_value={}, input_type=dict]`

**Root Cause**: The `get_full_tools_list()` function was calling `mcp_client.list_tools_sync()` which returned an empty dictionary `{}` instead of a proper tools list, causing a Pydantic validation error.

**Fix Applied**:
- Enhanced `get_full_tools_list()` function to handle different response formats
- Added proper error handling for empty responses
- Added type checking for dict vs list responses
- Added fallback to empty list when tools are not available

```python
def get_full_tools_list(mcp_client):
    """Get all available tools from MCP client."""
    try:
        if mcp_client:
            tools_result = mcp_client.list_tools_sync()
            # Handle different response formats
            if isinstance(tools_result, dict):
                # If it's a dict, look for 'tools' key
                if 'tools' in tools_result:
                    return tools_result['tools']
                else:
                    print("ℹ️  MCP client returned empty tools dict")
                    return []
            elif isinstance(tools_result, list):
                # If it's already a list, return it
                return tools_result
            else:
                print(f"⚠️  Unexpected MCP tools format: {type(tools_result)}")
                return []
        return []
    except Exception as e:
        print(f"⚠️  Could not get MCP tools: {e}")
        return []
```

#### 2. Memory Initialization Error
**Error**: `ℹ️  Memory not available - hooks disabled`

**Root Cause**: The memory initialization functions were trying to access global variables that weren't properly initialized, and the function signatures didn't match the expected parameters.

**Fixes Applied**:

##### A. Updated `create_or_get_memory_resource()` function
- Changed from accessing global variables to accepting parameters
- Added proper parameter passing for memory client and name

```python
def create_or_get_memory_resource(client: MemoryClient, memory_name: str):
    """Factory function for memory resource creation."""
    memory_manager = MemoryManager(client, memory_name)
    return memory_manager.get_or_create_memory()
```

##### B. Updated `initialize_memory()` function
- Added memory client parameter
- Added proper memory name retrieval from configuration
- Improved error handling

```python
def initialize_memory(client: MemoryClient) -> str | None:
    """Initialize memory with proper error handling."""
    try:
        memory_name = AgentConfig.MEMORY_NAME
        memory_id = create_or_get_memory_resource(client, memory_name)
        if memory_id:
            logger.info(f"AgentCore Memory ready with ID: {memory_id}")
            return memory_id
        else:
            _log_memory_initialization_error()
            return None
    except Exception as e:
        logger.error(f"Unexpected error during memory initialization: {e}")
        _log_memory_initialization_error()
        return None
```

### Configuration Changes

#### SSM Parameter Updates
All SSM parameters now use the `/app/eksagent/` prefix:
- `/app/eksagent/agentcore/memory_id`
- `/app/eksagent/agentcore/machine_client_id`
- `/app/eksagent/agentcore/cognito_discovery_url`
- `/app/eksagent/agentcore/gateway_iam_role`

#### Memory Configuration
- **Memory Name**: Changed from "DevOpsAgentMemory" to "EKSAgentMemory"
- **User ID**: Changed from "devops_001" to "eks_001"
- **Namespaces**: Updated to use "agent/eks/{actorId}/" prefix

## Prometheus Agent Improvements

### Overview
The Prometheus agent has been enhanced with optimized model settings, improved MCP error handling, and robust resource management for better performance and reliability in monitoring and observability tasks.

### Key Improvements Added

#### 1. Model Configuration Optimization
- **MAX_TOKENS**: Set to 4096 for comprehensive Prometheus analysis and troubleshooting
- **TOP_P**: Set to 0.9 for balanced creativity while maintaining technical accuracy  
- **Temperature**: Maintained at 0.3 for consistent, deterministic responses
- **Monitoring-Tuned**: Settings specifically optimized for monitoring and observability tasks

#### 2. Enhanced MCP Error Handling
- **Smart Error Detection**: Identifies common MCP validation errors and provides clean messages
- **User-Friendly Messages**: Replaces technical stack traces with informative status messages
- **Graceful Degradation**: Agent continues working even when MCP tools are unavailable
- **Multiple Fallback Mechanisms**: Robust error recovery for various failure scenarios

#### 3. Improved AWSMCPManager
- **Enhanced Error Handling**: Clean error messages for MCP tool failures
- **Response Format Handling**: Properly handles empty dicts, None responses, and various formats
- **Timeout Management**: Prevents hanging during MCP client initialization
- **Resource Cleanup**: Proper cleanup of stdio processes and connections

### Prometheus Agent Exit Hang Fix

#### Problem Summary
The Prometheus AgentCore agent was hanging indefinitely when users typed 'exit', requiring force termination. This was a critical usability issue preventing normal agent shutdown.

#### Root Cause Analysis

##### 1. Region Initialization Issue
- `use_manual_gateway()` function was trying to use global `REGION` variable before it was initialized
- This caused `NoRegionError` during gateway initialization
- **Fix**: Modified function to accept region parameter with fallback logic

##### 2. MCP Server Initialization Hangs
- Several AWS MCP servers were hanging during initialization:
  - `awslabs.prometheus-mcp-server`
  - `aws-knowledge-mcp-server` 
  - `awslabs.cloudwatch-mcp-server`
- These servers would block indefinitely during `client.start()` calls
- **Fix**: Added aggressive timeouts (2-5 seconds) with daemon threads

##### 3. Cleanup Process Hanging
- MCP client cleanup operations could hang waiting for unresponsive processes
- No timeout mechanism for cleanup operations
- **Fix**: Added 3-second timeout with force exit fallback

#### Solutions Implemented

##### 1. Region Parameter Fix
```python
def use_manual_gateway(region=None):
    """Use manually created gateway from AWS Management Console."""
    # Use provided region or fall back to global REGION or default
    if region is None:
        region = globals().get('REGION', 'us-east-1')
    
    gateway_client = boto3.client("bedrock-agentcore-control", region_name=region)
```

##### 2. MCP Client Timeout System
```python
def _initialize_single_mcp_client(self, server_name: str, server_config: dict):
    """Initialize a single MCP client with timeout."""
    # Use different timeouts based on server type
    problematic_servers = {
        'awslabs.prometheus-mcp-server',
        'aws-knowledge-mcp-server', 
        'awslabs.cloudwatch-mcp-server'
    }
    
    timeout = 2.0 if server_name in problematic_servers else 5.0
    
    # Run initialization with timeout
    init_thread = threading.Thread(target=init_client_worker, daemon=True)
    init_thread.start()
    init_thread.join(timeout=timeout)
    
    if init_thread.is_alive():
        print(f"⚠️  {server_name} initialization timed out after {timeout}s, skipping...")
        return
```

##### 3. Aggressive Cleanup Timeouts
```python
def cleanup_all_resources():
    """Cleanup all MCP resources and connections with timeout."""
    def cleanup_with_timeout():
        # Perform cleanup operations
        pass
    
    # Run cleanup with timeout to prevent hanging
    cleanup_thread = threading.Thread(target=cleanup_with_timeout, daemon=True)
    cleanup_thread.start()
    cleanup_thread.join(timeout=3.0)  # 3 second timeout
    
    if cleanup_thread.is_alive():
        print("⚠️  Cleanup timed out, forcing exit...")
        # Force exit if cleanup hangs
        os._exit(0)
```

### Prometheus Agent Resource Cleanup Implementation

#### Changes Made

##### 1. Fixed Memory Initialization Error
- **Problem**: `NameError: name 'memory_name' is not defined` during memory initialization
- **Location**: `create_or_get_memory_resource()` function (line 1368)
- **Root Cause**: Function was trying to use undefined variable `memory_name` instead of the configured constant
- **Solution**: Changed `memory_name` to `AgentConfig.MEMORY_NAME`
- **Result**: Memory initialization now works correctly without undefined variable errors

##### 2. Fixed Duplicate Output Issue (Initialization)
- **Problem**: Agent initialization and command line argument processing was happening at module import time, causing duplicate output
- **Root Cause**: Command line argument checking code (lines 409-430) was running at module level instead of being protected by `if __name__ == "__main__"`
- **Solution**: 
  - Moved command line argument processing into `handle_command_line_args()` function
  - Added call to `handle_command_line_args()` at the beginning of `main()` function
  - Moved all initialization code from module level to `initialize_agent()` function
- **Result**: Clean imports with no duplicate output, command line arguments still work when running directly

##### 2b. Fixed Runtime Duplicate Output Issue
- **Problem**: Agent responses were being displayed twice during conversation
- **Root Cause**: Strands framework logging was set to INFO level, causing it to output agent responses in addition to the conversation loop's print statement
- **Investigation Method**: Added unique response IDs to track duplication source
  - Responses appeared once with debug ID (from conversation loop) and once without (from strands logging)
- **Solution**: Changed strands logging level from INFO to WARNING: `logging.getLogger("strands").setLevel(logging.WARNING)`
- **Result**: Agent responses now appear only once, eliminating duplicate output

##### 3. Enhanced AWSMCPManager Cleanup
- **File**: `prometheus-agentcore/agent.py`
- **Location**: `AWSMCPManager.cleanup()` method
- **Improvements**:
  - Added detailed logging for each cleanup step
  - Enhanced stdio process termination with multiple fallback methods
  - Added graceful termination with `process.terminate()` followed by `process.kill()` if needed
  - Checks multiple possible locations for the underlying process object
  - Prevents double cleanup with `_cleanup_registered` flag
  - Added context manager support (`__enter__` and `__exit__`)

#### Testing Results

##### Before Fix
```bash
🧪 Testing agent exit behavior...
   • Agent process started
   • Sending 'exit' command...
❌ Agent exit test FAILED - process hung and had to be killed
```

##### After Fix
```bash
🧪 Testing agent exit behavior...
   • Agent process started
   • Sending 'exit' command...
   • Process exited with code: 0
   • Last few lines of output:
     🚀 AWS-Prometheus-agent: Ask me about Prometheus and AWS! Type 'exit' to quit.
     💡 Special commands: /tool or /tools (list MCP tools), /help (show commands)
     You >
✅ Agent exit test PASSED - no hanging detected
```

#### Performance Improvements

| Component | Before | After | Improvement |
|-----------|--------|-------|-------------|
| MCP Init Timeout | 30s | 15s | 50% faster |
| Problematic Servers | 10s | 2s | 80% faster |
| Cleanup Timeout | ∞ (hung) | 3s | Prevents hanging |
| Exit Time | ∞ (hung) | <5s | Immediate exit |

## Common Improvements Across All Agents

### 1. Model Configuration Optimization
All agents now use optimized Claude model settings:
- **Temperature: 0.3** - Deterministic responses for consistent troubleshooting
- **Max Tokens: 4096** - Sufficient for detailed analysis and comprehensive responses
- **Top-P: 0.9** - Balanced creativity for problem-solving while maintaining technical accuracy

### 2. Enhanced MCP Error Handling
- **Smart Error Detection** - Identifies common MCP validation errors
- **Clean Error Messages** - User-friendly error reporting instead of technical stack traces
- **Graceful Degradation** - Agents continue working even when MCP tools are unavailable
- **Multiple Fallback Mechanisms** - Robust error recovery for various failure scenarios

### 3. Memory Management Enhancements
- **Agent-Specific Memory Names** - Each agent has its own memory namespace
- **Proper Resource Cleanup** - Automatic cleanup on agent shutdown
- **Error Recovery** - Graceful handling of memory service unavailability
- **Context Retention** - Better conversation history and context management

### 4. Robust Error Recovery
- **MCP Validation Errors** - Specific handling for Pydantic validation errors
- **Connection Timeouts** - Graceful handling of MCP server connection issues
- **Fallback Mechanisms** - Multiple layers of error recovery
- **Clean Status Messages** - User-friendly error reporting

## Testing and Validation

### Comprehensive Test Results
All agents have been tested and validated to:
- ✅ Eliminate Pydantic validation errors for MCP tools
- ✅ Properly initialize memory when credentials are available
- ✅ Provide clear status messages about component availability
- ✅ Maintain backward compatibility with existing functionality
- ✅ Handle exit scenarios gracefully without hanging
- ✅ Provide enhanced error messages and recovery

### Expected Benefits
1. **Better User Experience** - Clean, informative error messages
2. **Enhanced Reliability** - Robust error handling and recovery
3. **Improved Performance** - Optimized model settings for infrastructure tasks
4. **Comprehensive Integration** - Full AWS service integration through MCP
5. **Future-Proof Architecture** - Maintainable and extensible design

## Usage

All enhanced agents maintain the same user interface while providing improved functionality:

```bash
# Run with current model
python3 {agent}-agentcore/agent.py

# Interactive model selection
python3 {agent}-agentcore/agent.py --select-model

# Setup gateway parameters
python3 {agent}-agentcore/agent.py setup

# Help and usage information
python3 {agent}-agentcore/agent.py --help
```

## Conclusion

The agent improvements provide a robust, scalable, and maintainable foundation for AWS infrastructure management. The enhancements focus on reliability, extensibility, and user experience while maintaining full backward compatibility across all agents in the telco project.