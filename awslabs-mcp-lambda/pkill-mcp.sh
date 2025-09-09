pkill -f "mcp-server\|mcp-proxy" && pkill -f "uv tool uvx.*mcp" && docker stop $(docker ps -q --filter ancestor=ghcr.io/github/github-mcp-server) 2>/dev/null || true
