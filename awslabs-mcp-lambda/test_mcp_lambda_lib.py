#!/usr/bin/env python3
"""
Test the mcp_lambda library to understand its API
"""

try:
    # Try to import the library
    import mcp_lambda
    print("✅ mcp_lambda imported successfully")
    print("Available attributes:", dir(mcp_lambda))
    
    # Try to import handlers
    try:
        from mcp_lambda import handlers
        print("✅ handlers module imported")
        print("Available handlers:", dir(handlers))
    except Exception as e:
        print("❌ handlers import error:", e)
    
    # Try specific handler
    try:
        from mcp_lambda.handlers import bedrock_agent_core_gateway_target_handler
        print("✅ bedrock handler module imported")
        print("Available functions:", dir(bedrock_agent_core_gateway_target_handler))
    except Exception as e:
        print("❌ bedrock handler import error:", e)
        
    # Try to see what's in the server_adapter
    try:
        from mcp_lambda import server_adapter
        print("✅ server_adapter imported")
        print("Available in server_adapter:", dir(server_adapter))
    except Exception as e:
        print("❌ server_adapter import error:", e)

except Exception as e:
    print("❌ Failed to import mcp_lambda:", e)
    
# Try to see what's actually installed
try:
    import pkg_resources
    dist = pkg_resources.get_distribution('run-mcp-servers-with-aws-lambda')
    print(f"✅ Package version: {dist.version}")
    print(f"✅ Package location: {dist.location}")
except Exception as e:
    print("❌ Package info error:", e)