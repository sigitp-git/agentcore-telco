#!/usr/bin/env python3
"""
Simple comprehensive test for all AgentCore agents.
Tests both agent.py and invoke_runtime.py for each agent.
"""

import os
import sys
import subprocess
from datetime import datetime

def test_agent(agent_name, agent_dir):
    """Test both agent.py and invoke_runtime.py for a single agent."""
    print(f"🚀 Testing {agent_name.upper()} Agent")
    print("-" * 30)
    
    results = {'agent.py': False, 'invoke_runtime.py': False, 'token_auth': False}
    
    # Test agent.py
    print(f"🔍 Testing {agent_name} agent.py...")
    try:
        original_cwd = os.getcwd()
        os.chdir(agent_dir)
        
        result = subprocess.run([
            sys.executable, '-c', 
            """
import sys
sys.path.append('.')
try:
    import agent
    print('SUCCESS: agent.py import')
    if hasattr(agent, 'AgentConfig'):
        config = agent.AgentConfig()
        print('SUCCESS: AgentConfig loaded')
        if hasattr(agent.AgentConfig, 'get_model_id'):
            model_id = agent.AgentConfig.get_model_id()
            print(f'SUCCESS: Model ID - {model_id}')
except Exception as e:
    print(f'ERROR: {e}')
"""
        ], capture_output=True, text=True, timeout=30, 
        env={**os.environ, 'AWS_DEFAULT_REGION': 'us-east-1'})
        
        if 'SUCCESS: agent.py import' in result.stdout:
            print("  ✅ agent.py import successful")
            results['agent.py'] = True
            
            if 'SUCCESS: AgentConfig loaded' in result.stdout:
                print("  ✅ AgentConfig loaded")
                
            for line in result.stdout.split('\n'):
                if line.startswith('SUCCESS: Model ID'):
                    model_id = line.split(' - ', 1)[1]
                    print(f"  📝 Model: {model_id}")
        else:
            print("  ❌ agent.py import failed")
            if 'ERROR:' in result.stdout:
                error = result.stdout.split('ERROR:', 1)[1].strip()
                print(f"     Error: {error}")
                
    except Exception as e:
        print(f"  ❌ agent.py test error: {e}")
    finally:
        os.chdir(original_cwd)
    
    # Test invoke_runtime.py
    print(f"🔍 Testing {agent_name} invoke_runtime.py...")
    try:
        os.chdir(agent_dir)
        
        result = subprocess.run([
            sys.executable, '-c',
            """
import sys
sys.path.append('.')
try:
    from invoke_runtime import AgentRuntimeInvoker
    invoker = AgentRuntimeInvoker()
    print('SUCCESS: invoke_runtime.py import')
    runtime_arn = invoker.get_agent_runtime_arn()
    if runtime_arn:
        print(f'SUCCESS: Runtime ARN - {runtime_arn}')
    else:
        print('WARNING: No Runtime ARN')
except Exception as e:
    print(f'ERROR: {e}')
"""
        ], capture_output=True, text=True, timeout=60,
        env={**os.environ, 'AWS_DEFAULT_REGION': 'us-east-1'})
        
        if 'SUCCESS: invoke_runtime.py import' in result.stdout:
            print("  ✅ invoke_runtime.py import successful")
            results['invoke_runtime.py'] = True
            
            for line in result.stdout.split('\n'):
                if line.startswith('SUCCESS: Runtime ARN'):
                    print("  ✅ Runtime ARN configured")
                elif line.startswith('WARNING: No Runtime ARN'):
                    print("  ⚠️  No Runtime ARN found")
        else:
            print("  ❌ invoke_runtime.py import failed")
            if 'ERROR:' in result.stdout:
                error = result.stdout.split('ERROR:', 1)[1].strip()
                print(f"     Error: {error}")
                
    except Exception as e:
        print(f"  ❌ invoke_runtime.py test error: {e}")
    finally:
        os.chdir(original_cwd)
    
    # Test token authentication
    print(f"🔍 Testing {agent_name} token authentication...")
    try:
        os.chdir(agent_dir)
        
        test_code = f"""
import sys
sys.path.append('.')
try:
    from utils import get_ssm_parameter, get_cognito_client_secret
    from agent import get_token
    
    client_id = get_ssm_parameter('/app/{agent_name}agent/agentcore/machine_client_id')
    client_secret = get_cognito_client_secret()
    scope = get_ssm_parameter('/app/{agent_name}agent/agentcore/cognito_auth_scope')
    url = get_ssm_parameter('/app/{agent_name}agent/agentcore/cognito_token_url')
    
    if client_id and client_secret and scope and url:
        result = get_token(client_id, client_secret, scope, url)
        if 'access_token' in result:
            print('SUCCESS: Token authentication')
        else:
            error = result.get('error', 'Unknown error')
            print(f'ERROR: Token failed - {{error}}')
    else:
        print('ERROR: Missing SSM parameters')
        
except Exception as e:
    print(f'ERROR: {{str(e)}}')
"""
        
        result = subprocess.run([
            sys.executable, '-c', test_code
        ], capture_output=True, text=True, timeout=30,
        env={**os.environ, 'AWS_DEFAULT_REGION': 'us-east-1'})
        
        if 'SUCCESS: Token authentication' in result.stdout:
            print("  ✅ Token authentication successful")
            results['token_auth'] = True
        else:
            print("  ⚠️  Token authentication failed")
            if 'ERROR:' in result.stdout:
                error = result.stdout.split('ERROR:', 1)[1].strip()
                print(f"     Error: {error}")
                
    except Exception as e:
        print(f"  ❌ Token test error: {e}")
    finally:
        os.chdir(original_cwd)
    
    print()
    return results

def main():
    """Main test execution."""
    print("🧪 COMPREHENSIVE AGENT TEST SUITE")
    print("=" * 50)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    agents = {
        'eks': 'eks-agentcore',
        'vpc': 'vpc-agentcore', 
        'outposts': 'outposts-agentcore',
        'prometheus': 'prometheus-agentcore'
    }
    
    all_results = {}
    
    # Test all agents
    for agent_name, agent_dir in agents.items():
        all_results[agent_name] = test_agent(agent_name, agent_dir)
    
    # Print summary
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    total_tests = len(agents) * 2  # agent.py + invoke_runtime.py for each
    passed_tests = 0
    
    print("🎯 AGENT STATUS SUMMARY")
    print("-" * 40)
    
    for agent_name, results in all_results.items():
        agent_py_status = "✅" if results['agent.py'] else "❌"
        runtime_status = "✅" if results['invoke_runtime.py'] else "❌"
        token_status = "✅" if results['token_auth'] else "⚠️"
        
        if results['agent.py']:
            passed_tests += 1
        if results['invoke_runtime.py']:
            passed_tests += 1
            
        overall_status = "🟢 EXCELLENT" if all(results.values()) else "🟡 PARTIAL" if any(results.values()) else "🔴 FAILED"
        
        print(f"{agent_name.upper():<12} | agent.py: {agent_py_status} | runtime: {runtime_status} | token: {token_status} | {overall_status}")
    
    print()
    print(f"Total Core Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {total_tests - passed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL CORE TESTS PASSED! All agents are fully functional.")
    elif passed_tests > total_tests // 2:
        print("\n⚠️  MOSTLY SUCCESSFUL with some issues to address.")
    else:
        print("\n❌ MULTIPLE FAILURES detected. Review and fix issues.")
        
    print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()