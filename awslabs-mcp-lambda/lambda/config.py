"""
MCP Server Configuration

Configure which MCP server to run in the Lambda wrapper.
"""

# Configuration for the MCP server to wrap
# This example uses the AWS Documentation MCP server
MCP_SERVER_CONFIG = {
    "command": "uvx",
    "args": ["awslabs.aws-documentation-mcp-server@latest"],
    "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
    }
}

# Alternative configurations for other MCP servers:

# Git MCP Server
# MCP_SERVER_CONFIG = {
#     "command": "uvx",
#     "args": ["mcp-server-git"],
#     "env": {}
# }

# Filesystem MCP Server
# MCP_SERVER_CONFIG = {
#     "command": "uvx",
#     "args": ["mcp-server-filesystem", "/tmp"],
#     "env": {}
# }

# Custom MCP Server (if you have a custom server script)
# MCP_SERVER_CONFIG = {
#     "command": "python",
#     "args": ["/opt/my_mcp_server.py"],
#     "env": {
#         "CUSTOM_ENV_VAR": "value"
#     }
# }