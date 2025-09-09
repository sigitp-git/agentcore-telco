#!/bin/bash
# Kill all local MCP server processes

pkill -f "awslabs\." && \
pkill -f "mcp-proxy" && \
pkill -f "uvx.*mcp" && \
docker stop $(docker ps -q --filter "ancestor=ghcr.io/github/github-mcp-server") 2>/dev/null || true

echo "All MCP server processes killed"
