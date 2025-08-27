#!/usr/bin/env python3
"""
Management script for Multi-MCP Lambda functions

This script provides common management operations for the multi-server setup.
"""

import argparse
import json
import os
import sys
import yaml
import subprocess
from pathlib import Path


def load_server_configs():
    """Load server configurations from servers.yaml"""
    with open('servers.yaml', 'r') as f:
        return yaml.safe_load(f)


def list_servers():
    """List all configured MCP servers."""
    config = load_server_configs()
    servers = config.get('servers', {})
    
    print("📋 Configured MCP Servers:")
    print("=" * 50)
    
    for server_id, server_config in servers.items():
        print(f"🔧 {server_id}")
        print(f"   Name: {server_config['name']}")
        print(f"   Command: {server_config['command']} {' '.join(server_config['args'])}")
        print(f"   Timeout: {server_config.get('timeout', 60)}s")
        print(f"   Memory: {server_config.get('memory', 1024)}MB")
        print(f"   Lambda Dir: lambda-{server_id}/")
        print()


def add_server():
    """Interactive server addition."""
    print("➕ Adding a new MCP server...")
    
    server_id = input("Server ID (e.g., 'my-server'): ").strip()
    if not server_id:
        print("❌ Server ID is required")
        return False
    
    name = input("Server Name: ").strip()
    if not name:
        print("❌ Server name is required")
        return False
    
    command = input("Command (e.g., 'uvx'): ").strip() or "uvx"
    args_input = input("Arguments (space-separated): ").strip()
    args = args_input.split() if args_input else []
    
    timeout = input("Timeout in seconds (default: 60): ").strip()
    timeout = int(timeout) if timeout.isdigit() else 60
    
    memory = input("Memory in MB (default: 1024): ").strip()
    memory = int(memory) if memory.isdigit() else 1024
    
    # Load existing config
    config = load_server_configs()
    
    # Add new server
    config['servers'][server_id] = {
        'name': name,
        'description': f"Custom MCP server: {name}",
        'command': command,
        'args': args,
        'env': {},
        'timeout': timeout,
        'memory': memory
    }
    
    # Save config
    with open('servers.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"✅ Added server '{server_id}' to servers.yaml")
    print("🔧 Run 'python3 generate_configs.py' to generate Lambda configuration")
    return True


def remove_server():
    """Interactive server removal."""
    config = load_server_configs()
    servers = config.get('servers', {})
    
    if not servers:
        print("❌ No servers configured")
        return False
    
    print("📋 Available servers:")
    for i, (server_id, server_config) in enumerate(servers.items(), 1):
        print(f"  {i}. {server_id} - {server_config['name']}")
    
    try:
        choice = int(input("\nSelect server to remove (number): ").strip())
        server_ids = list(servers.keys())
        
        if 1 <= choice <= len(server_ids):
            server_id = server_ids[choice - 1]
            
            # Confirm removal
            confirm = input(f"Remove '{server_id}'? (y/N): ").strip().lower()
            if confirm == 'y':
                del config['servers'][server_id]
                
                # Save config
                with open('servers.yaml', 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, indent=2)
                
                # Remove Lambda directory if it exists
                lambda_dir = f"lambda-{server_id}"
                if os.path.exists(lambda_dir):
                    import shutil
                    shutil.rmtree(lambda_dir)
                    print(f"🗑️  Removed Lambda directory: {lambda_dir}")
                
                print(f"✅ Removed server '{server_id}'")
                print("🔧 Run 'python3 generate_configs.py' to update configurations")
                return True
            else:
                print("❌ Removal cancelled")
                return False
        else:
            print("❌ Invalid selection")
            return False
            
    except (ValueError, KeyboardInterrupt):
        print("❌ Invalid input or cancelled")
        return False


def test_server(server_id=None):
    """Test specific server or all servers."""
    if server_id:
        # Test specific server
        lambda_dir = f"lambda-{server_id}"
        if not os.path.exists(lambda_dir):
            print(f"❌ Lambda directory not found: {lambda_dir}")
            return False
        
        print(f"🧪 Testing server: {server_id}")
        result = subprocess.run([
            sys.executable, "test_multi.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Server {server_id} test passed")
            return True
        else:
            print(f"❌ Server {server_id} test failed")
            print(result.stdout)
            print(result.stderr)
            return False
    else:
        # Test all servers
        print("🧪 Testing all servers...")
        result = subprocess.run([
            sys.executable, "test_multi.py"
        ])
        return result.returncode == 0


def deploy():
    """Deploy all Lambda functions."""
    print("🚀 Deploying all Lambda functions...")
    
    # Generate configs first
    print("🔧 Generating configurations...")
    result = subprocess.run([sys.executable, "generate_configs.py"])
    if result.returncode != 0:
        print("❌ Failed to generate configurations")
        return False
    
    # Deploy
    print("🚀 Deploying to AWS...")
    result = subprocess.run(["./deploy_multi.sh"])
    return result.returncode == 0


def status():
    """Show deployment status."""
    print("📊 Multi-MCP Lambda Status")
    print("=" * 40)
    
    config = load_server_configs()
    servers = config.get('servers', {})
    
    print(f"📋 Configured servers: {len(servers)}")
    
    # Check Lambda directories
    generated = 0
    for server_id in servers.keys():
        lambda_dir = f"lambda-{server_id}"
        if os.path.exists(lambda_dir):
            generated += 1
    
    print(f"🔧 Generated Lambda configs: {generated}/{len(servers)}")
    
    # Check if deployed (this would require AWS CLI calls)
    print("☁️  Deployment status: Use 'aws lambda list-functions' to check")
    
    print("\n📁 Lambda directories:")
    for server_id in servers.keys():
        lambda_dir = f"lambda-{server_id}"
        status = "✅" if os.path.exists(lambda_dir) else "❌"
        print(f"  {status} {lambda_dir}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Manage Multi-MCP Lambda functions")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List all configured servers')
    
    # Add command
    subparsers.add_parser('add', help='Add a new MCP server')
    
    # Remove command
    subparsers.add_parser('remove', help='Remove an MCP server')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test servers')
    test_parser.add_argument('server_id', nargs='?', help='Specific server to test')
    
    # Deploy command
    subparsers.add_parser('deploy', help='Deploy all Lambda functions')
    
    # Status command
    subparsers.add_parser('status', help='Show deployment status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'list':
            list_servers()
        elif args.command == 'add':
            add_server()
        elif args.command == 'remove':
            remove_server()
        elif args.command == 'test':
            test_server(getattr(args, 'server_id', None))
        elif args.command == 'deploy':
            deploy()
        elif args.command == 'status':
            status()
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
            
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")
        return 1
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())