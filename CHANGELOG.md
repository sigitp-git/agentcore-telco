# Changelog

All notable changes to the AWS AgentCore Telco project will be documented in this file.

## [Unreleased] - 2025-08-29

### Added
- **MCP Integration Guide**: Comprehensive documentation for Model Context Protocol fixes
- **52 AWS MCP Tools**: Full integration with AWS services through MCP protocol
- **Enhanced Logging Control**: Comprehensive logging suppression for clean output
- **MCP Configuration Management**: Tools for managing MCP server configuration

### Fixed
- **MCP Tools Loading**: Resolved MCP tools not loading from mcp.json configuration
  - Fixed `ENABLE_AWS_MCP = False` to `True` in Prometheus agent
  - Set correct `AWS_MCP_CONFIG_PATH` to mcp.json file location
  - All 7 MCP servers now loading successfully (52 tools total)
- **Duplicate Output Issue**: Eliminated verbose logging causing duplicate responses
  - Changed Prometheus MCP server from DEBUG to ERROR log level
  - Added comprehensive logging suppression in agent code
  - Clean, single-line responses without duplicate output
- **MCP Server Configuration**: Enhanced mcp.json configuration
  - Removed duplicate autoApprove entries
  - Added proper AWS region environment variables
  - Optimized logging levels for all MCP servers

### Changed
- **Prometheus Agent Configuration**: Updated MCP integration settings
  - `ENABLE_AWS_MCP = True` (was False)
  - `AWS_MCP_CONFIG_PATH` now points to correct mcp.json file
  - Enhanced logging suppression for multiple AWS services
- **MCP Server Logging**: Standardized logging across all MCP servers
  - All servers now use ERROR level logging by default
  - Added environment variables for additional logging control
  - Improved initialization timeouts for problematic servers

### Improved
- **User Experience**: Clean agent output without verbose MCP logging
- **Performance**: Optimized MCP server initialization with proper timeouts
- **Documentation**: Updated README with MCP integration details
- **Security**: Verified no security issues in MCP configuration changes

### Security
- **Configuration Review**: ✅ No security issues identified
  - MCP configuration contains no sensitive information
  - Proper AWS credential handling through IAM roles
  - No hardcoded secrets or credentials in configuration files

## [Previous] - 2024-12-XX

### Added
- **Agent2Agent Type System**: Complete type definitions in `agent2agent/types.py`
  - `AgentCard`, `AgentCapabilities`, `AgentSkill`, `AgentProvider` classes
  - `Message`, `TextPart`, `Role` for structured communication
  - `A2ARequest`, `A2AResponse` for request/response patterns
  - Utility functions for creating messages and capabilities
  - Full validation and error handling for all types

### Fixed
- **A2A Import Issues**: Resolved `ModuleNotFoundError: No module named 'a2a'`
  - Updated import statements in `agent2agent/wrappers/eks_a2a_wrapper.py`
  - Changed from `from a2a.types import` to `from agent2agent.types import`
  - Created missing `agent2agent/types.py` module with all required classes
  - Updated `agent2agent/__init__.py` to properly expose types module

### Changed
- **Documentation Updates**: Comprehensive documentation refresh
  - Updated main `README.md` with A2A type system information
  - Enhanced `agent2agent/README.md` with type examples and usage
  - Updated `agent2agent/QUICK_START.md` with correct import statements
  - Added recent updates section to main documentation
  - Updated project structure diagrams to include `types.py`

### Improved
- **A2A Integration**: Enhanced cross-agent communication
  - Working A2A integration examples with proper type safety
  - Comprehensive agent card creation with validation
  - Structured message passing between agents
  - Enhanced troubleshooting workflows with multi-agent collaboration

## Previous Changes

### Agent Framework Foundation
- Initial implementation of EKS, VPC, Outposts, and Prometheus agents
- Amazon Bedrock AgentCore integration
- AWS Cognito authentication
- Streamlit web interfaces for all agents
- Comprehensive test suite
- Environment configuration management
- SSM parameter store integration

### Core Features
- Multi-model Claude support (Sonnet 4, 3.7 Sonnet, 3.5 Sonnet v1/v2, 3.5 Haiku)
- MCP (Model Context Protocol) integration
- Memory management with AgentCore
- DuckDuckGo search integration
- Structured logging and error handling
- Docker containerization support

---

## Version Format

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backwards compatible manner  
- **PATCH**: Backwards compatible bug fixes

## Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes