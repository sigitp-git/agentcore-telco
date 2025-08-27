#!/usr/bin/env python3
"""
Generate MCP tool schemas for all AWS Labs MCP servers.

This script reads the servers.yaml configuration and generates tool schemas
for each AWS Labs MCP server using the MCP inspector.
"""

import yaml
import subprocess
import os
import sys
from pathlib import Path
import concurrent.futures
import time

def load_servers_config(config_file="servers.yaml"):
    """Load server configurations from YAML file."""
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('servers', {})

def extract_package_name(args):
    """Extract the package name from uvx args."""
    for arg in args:
        if arg.startswith('awslabs.'):
            # Remove @latest or other version specifiers
            package = arg.split('@')[0]
            return package
    return None

def generate_schema(server_id, package_name, output_dir):
    """Generate schema for a single MCP server."""
    try:
        print(f"🔄 Generating schema for {server_id} ({package_name})...")
        
        # Create output filename
        output_file = output_dir / f"{server_id}-awslabs-tool-schema.json"
        
        # Build the command
        cmd = [
            "npx", "@modelcontextprotocol/inspector",
            "--cli", "--method", "tools/list",
            "uvx", package_name
        ]
        
        # Run the command with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0:
            # Write the output to file
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            print(f"✅ Generated schema for {server_id}")
            return True, server_id, None
        else:
            error_msg = f"Command failed with return code {result.returncode}: {result.stderr}"
            print(f"❌ Failed to generate schema for {server_id}: {error_msg}")
            return False, server_id, error_msg
            
    except subprocess.TimeoutExpired:
        error_msg = "Command timed out after 2 minutes"
        print(f"⏰ Timeout generating schema for {server_id}: {error_msg}")
        return False, server_id, error_msg
    except Exception as e:
        error_msg = str(e)
        print(f"💥 Exception generating schema for {server_id}: {error_msg}")
        return False, server_id, error_msg

def main():
    """Main function to generate all schemas."""
    print("🚀 Starting MCP schema generation...")
    
    # Create output directory
    output_dir = Path("mcp-schemas")
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory: {output_dir.absolute()}")
    
    # Load server configurations
    try:
        servers = load_servers_config()
        print(f"📋 Loaded {len(servers)} server configurations")
    except Exception as e:
        print(f"❌ Failed to load servers.yaml: {e}")
        sys.exit(1)
    
    # Filter AWS Labs servers
    awslabs_servers = {}
    for server_id, config in servers.items():
        if config.get('command') == 'uvx':
            args = config.get('args', [])
            package_name = extract_package_name(args)
            if package_name:
                awslabs_servers[server_id] = {
                    'package': package_name,
                    'config': config
                }
    
    print(f"🔍 Found {len(awslabs_servers)} AWS Labs MCP servers:")
    for server_id, info in awslabs_servers.items():
        print(f"  - {server_id}: {info['package']}")
    
    if not awslabs_servers:
        print("❌ No AWS Labs MCP servers found!")
        sys.exit(1)
    
    # Generate schemas with parallel processing
    print(f"\n🔄 Generating schemas (max 3 concurrent processes)...")
    
    successful = []
    failed = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks
        future_to_server = {
            executor.submit(
                generate_schema, 
                server_id, 
                info['package'], 
                output_dir
            ): server_id 
            for server_id, info in awslabs_servers.items()
        }
        
        # Process completed tasks
        for future in concurrent.futures.as_completed(future_to_server):
            server_id = future_to_server[future]
            try:
                success, srv_id, error = future.result()
                if success:
                    successful.append(srv_id)
                else:
                    failed.append((srv_id, error))
            except Exception as e:
                failed.append((server_id, str(e)))
    
    # Print summary
    print(f"\n📊 Schema Generation Summary:")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        print(f"\n✅ Successfully generated schemas for:")
        for server_id in successful:
            schema_file = output_dir / f"{server_id}-awslabs-tool-schema.json"
            print(f"  - {server_id}: {schema_file}")
    
    if failed:
        print(f"\n❌ Failed to generate schemas for:")
        for server_id, error in failed:
            print(f"  - {server_id}: {error}")
    
    # List generated files
    schema_files = list(output_dir.glob("*-awslabs-tool-schema.json"))
    print(f"\n📁 Generated {len(schema_files)} schema files in {output_dir}/")
    
    if len(schema_files) > 0:
        print("🎉 Schema generation completed!")
        return 0
    else:
        print("💥 No schemas were generated successfully!")
        return 1

if __name__ == "__main__":
    sys.exit(main())