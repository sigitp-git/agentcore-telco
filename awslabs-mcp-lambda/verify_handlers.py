#!/usr/bin/env python3
"""
Verify all generated lambda handlers have the correct structure and imports.
"""

import os
import ast
from pathlib import Path

def check_handler_file(handler_path):
    """Check if a lambda handler file has the correct structure"""
    try:
        with open(handler_path, 'r') as f:
            content = f.read()
        
        # Parse the Python file
        tree = ast.parse(content)
        
        # Check for required imports
        required_imports = [
            'boto3',
            'BedrockAgentCoreGatewayTargetHandler',
            'StdioServerAdapterRequestHandler',
            'StdioServerParameters'
        ]
        
        imports_found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports_found.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports_found.append(alias.name)
        
        # Check for required classes and functions
        classes_found = []
        functions_found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes_found.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions_found.append(node.name)
        
        # Verify structure
        issues = []
        
        for required_import in required_imports:
            if required_import not in str(imports_found):
                issues.append(f"Missing import: {required_import}")
        
        if 'MockClientContext' not in classes_found:
            issues.append("Missing MockClientContext class")
        
        if 'lambda_handler' not in functions_found:
            issues.append("Missing lambda_handler function")
        
        # Check for key patterns in content
        if 'session.get_credentials()' not in content:
            issues.append("Missing AWS credentials extraction")
        
        if 'StdioServerParameters(' not in content:
            issues.append("Missing StdioServerParameters usage")
        
        if 'BedrockAgentCoreGatewayTargetHandler(' not in content:
            issues.append("Missing BedrockAgentCoreGatewayTargetHandler usage")
        
        return issues
        
    except Exception as e:
        return [f"Error parsing file: {str(e)}"]

def main():
    """Verify all lambda handlers"""
    print("🔍 Verifying all MCP Lambda handlers...")
    
    handlers_dir = Path("lambda_handlers_q")
    if not handlers_dir.exists():
        print("❌ lambda_handlers_q directory not found!")
        return
    
    total_handlers = 0
    valid_handlers = 0
    
    for handler_dir in handlers_dir.iterdir():
        if handler_dir.is_dir():
            lambda_file = handler_dir / "lambda_function.py"
            if lambda_file.exists():
                total_handlers += 1
                print(f"\n📁 Checking {handler_dir.name}...")
                
                issues = check_handler_file(lambda_file)
                if not issues:
                    print(f"  ✅ {handler_dir.name} - All checks passed")
                    valid_handlers += 1
                else:
                    print(f"  ❌ {handler_dir.name} - Issues found:")
                    for issue in issues:
                        print(f"    - {issue}")
    
    print(f"\n📊 Summary:")
    print(f"  Total handlers: {total_handlers}")
    print(f"  Valid handlers: {valid_handlers}")
    print(f"  Success rate: {valid_handlers/total_handlers*100:.1f}%")
    
    if valid_handlers == total_handlers:
        print("\n🎉 All handlers are correctly structured!")
    else:
        print(f"\n⚠️  {total_handlers - valid_handlers} handlers need attention")

if __name__ == "__main__":
    main()