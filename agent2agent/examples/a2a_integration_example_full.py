#!/usr/bin/env python3
"""
Example: A2A Integration with EKS Agent
Shows how the EKS agent can collaborate with other telco agents
"""

import asyncio
import json
import sys
import os

# Add the project root to the path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from agent2agent.wrappers.eks_a2a_wrapper import EKSA2AWrapper

class MockEKSAgent:
    """Mock EKS Agent for example"""
    
    def __init__(self):
        self.name = "EKS-Agent"
        self.version = "1.0.0"

async def example_a2a_integration():
    """Example A2A integration capabilities"""
    
    print("🌐 A2A Integration Example with EKS Agent")
    print("=" * 60)
    
    # Create mock EKS agent and A2A wrapper
    eks_agent = MockEKSAgent()
    a2a_wrapper = EKSA2AWrapper(eks_agent)
    
    print(f"✅ Initialized {a2a_wrapper.agent_card.name}")
    print(f"   Version: {a2a_wrapper.agent_card.version}")
    print(f"   Skills: {len(a2a_wrapper.agent_card.skills)} available")
    print(f"   URL: {a2a_wrapper.agent_card.url}")
    
    # Display agent capabilities
    print(f"\n🎯 Agent Capabilities:")
    for skill in a2a_wrapper.agent_card.skills:
        print(f"   • {skill.name}: {skill.description}")
    
    # Display agent registry
    print(f"\n🔍 Discovered Agents:")
    for agent_name, agent_url in a2a_wrapper.agent_registry.items():
        print(f"   • {agent_name}: {agent_url}")
    
    print(f"\n" + "=" * 60)
    print("🚀 EXAMPLE: Enhanced Pod Troubleshooting with Cross-Agent Collaboration")
    print("=" * 60)
    
    # Example enhanced pod troubleshooting
    result = await a2a_wrapper.enhanced_pod_troubleshooting(
        pod_name="web-app-frontend-abc123",
        namespace="production", 
        cluster_name="prod-eks-cluster"
    )
    
    print(f"\n📋 TROUBLESHOOTING RESULTS:")
    print("=" * 40)
    
    # Display pod diagnosis
    pod_diag = result.get("pod_diagnosis", {})
    print(f"🔍 Pod Diagnosis:")
    print(f"   Status: {pod_diag.get('diagnosis', {}).get('status', 'Unknown')}")
    print(f"   Issues: {', '.join(pod_diag.get('diagnosis', {}).get('issues_detected', []))}")
    
    # Display cross-agent analysis
    cross_analysis = result.get("cross_agent_analysis", {})
    
    if "metrics" in cross_analysis:
        metrics = cross_analysis["metrics"]
        print(f"\n📊 Metrics Analysis (from Prometheus Agent):")
        cluster_health = metrics.get("metrics", {}).get("cluster_health", {})
        print(f"   Nodes Ready: {cluster_health.get('nodes_ready', 0)}/{cluster_health.get('node_count', 0)}")
        print(f"   Pods Running: {cluster_health.get('pods_running', 0)}")
        print(f"   Pods Failed: {cluster_health.get('pods_failed', 0)}")
        
        alerts = metrics.get("metrics", {}).get("alerts", [])
        if alerts:
            print(f"   Active Alerts: {len(alerts)}")
            for alert in alerts:
                print(f"     - {alert.get('severity', '').upper()}: {alert.get('alert', '')}")
    
    if "vpc_analysis" in cross_analysis:
        vpc = cross_analysis["vpc_analysis"]
        print(f"\n🌐 VPC Analysis (from VPC Agent):")
        analysis = vpc.get("analysis", {})
        
        sg_issues = analysis.get("security_groups", {}).get("issues", [])
        if sg_issues:
            print(f"   Security Group Issues: {', '.join(sg_issues)}")
        
        dns_status = analysis.get("dns", {})
        print(f"   DNS Resolution: {'✅' if dns_status.get('vpc_dns_resolution') else '❌'}")
    
    # Display comprehensive recommendations
    recommendations = result.get("comprehensive_recommendations", [])
    print(f"\n💡 Comprehensive Recommendations ({len(recommendations)} items):")
    for i, rec in enumerate(recommendations[:8], 1):  # Show first 8
        urgency = "🚨" if "URGENT" in rec else "💡"
        print(f"   {urgency} {rec}")
    
    if len(recommendations) > 8:
        print(f"   ... and {len(recommendations) - 8} more recommendations")
    
    print(f"\n" + "=" * 60)
    print("🎯 A2A INTEGRATION BENEFITS SHOWN")
    print("=" * 60)
    
    benefits = [
        "Cross-agent capability discovery and communication",
        "Enhanced troubleshooting with multi-domain context",
        "Automated collaboration between EKS, VPC, and Prometheus agents", 
        "Comprehensive recommendations from combined analysis",
        "Reduced manual coordination between infrastructure teams",
        "Faster incident resolution with richer context"
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"{i}. ✅ {benefit}")
    
    print(f"\n🔧 NEXT STEPS:")
    print("1. Deploy A2A server endpoints for each agent")
    print("2. Implement real A2A client communication")
    print("3. Add authentication and security")
    print("4. Set up agent discovery service")
    print("5. Monitor cross-agent communication health")

async def example_individual_agent_requests():
    """Example individual A2A requests to other agents"""
    
    print(f"\n" + "=" * 60)
    print("🔄 EXAMPLE: Individual A2A Agent Requests")
    print("=" * 60)
    
    eks_agent = MockEKSAgent()
    a2a_wrapper = EKSA2AWrapper(eks_agent)
    
    # Example VPC Agent request
    print("1. 🌐 Requesting VPC network analysis...")
    vpc_response = await a2a_wrapper.send_request_to_agent("VPC-Agent", {
        "action": "analyze_network_connectivity",
        "vpc_id": "vpc-prod-123",
        "issue_description": "EKS pod connectivity issues"
    })
    
    if vpc_response:
        print(f"   ✅ VPC Agent Response:")
        print(f"      Security Group Issues: {len(vpc_response.get('analysis', {}).get('security_groups', {}).get('issues', []))}")
        print(f"      Recommendations: {len(vpc_response.get('recommendations', []))}")
    
    # Example Prometheus Agent request
    print("\n2. 📊 Requesting cluster metrics...")
    metrics_response = await a2a_wrapper.send_request_to_agent("Prometheus-Agent", {
        "action": "get_cluster_metrics",
        "cluster_name": "prod-eks-cluster",
        "timeframe": "1h"
    })
    
    if metrics_response:
        print(f"   ✅ Prometheus Agent Response:")
        cluster_health = metrics_response.get("metrics", {}).get("cluster_health", {})
        print(f"      Cluster Health: {cluster_health.get('pods_running', 0)} pods running")
        print(f"      Active Alerts: {len(metrics_response.get('metrics', {}).get('alerts', []))}")
    
    # Example Outposts Agent request
    print("\n3. 🏢 Requesting hybrid connectivity check...")
    outposts_response = await a2a_wrapper.send_request_to_agent("Outposts-Agent", {
        "action": "check_hybrid_connectivity",
        "outpost_id": "op-12345678",
        "cluster_name": "hybrid-eks-cluster"
    })
    
    if outposts_response:
        print(f"   ✅ Outposts Agent Response:")
        connectivity = outposts_response.get("connectivity", {})
        print(f"      Region Connection: {connectivity.get('aws_region_connection', 'unknown')}")
        print(f"      Latency: {connectivity.get('latency_to_region', 'unknown')}")

async def example_agent_card_details():
    """Example detailed agent card information"""
    
    print(f"\n" + "=" * 60)
    print("📋 EXAMPLE: Agent Card Details")
    print("=" * 60)
    
    eks_agent = MockEKSAgent()
    a2a_wrapper = EKSA2AWrapper(eks_agent)
    
    card = a2a_wrapper.agent_card
    
    print(f"Agent Name: {card.name}")
    print(f"Version: {card.version}")
    print(f"Description: {card.description}")
    print(f"Provider: {card.provider.organization}")
    print(f"URL: {card.url}")
    
    print(f"\nCapabilities:")
    print(f"  • Streaming: {card.capabilities.streaming}")
    print(f"  • Push Notifications: {card.capabilities.push_notifications}")
    print(f"  • State History: {card.capabilities.state_transition_history}")
    
    print(f"\nInput/Output Modes:")
    print(f"  • Input: {', '.join(card.default_input_modes)}")
    print(f"  • Output: {', '.join(card.default_output_modes)}")
    
    print(f"\nSkills ({len(card.skills)} total):")
    for skill in card.skills:
        print(f"  • {skill.name}")
        print(f"    Description: {skill.description}")
        print(f"    Tags: {', '.join(skill.tags)}")
        print()

async def main():
    """Main example function"""
    
    try:
        await example_a2a_integration()
        await example_individual_agent_requests()
        await example_agent_card_details()
        
        print(f"\n🎉 A2A Integration Example Complete!")
        print("The EKS agent is now ready for cross-agent collaboration!")
        
    except KeyboardInterrupt:
        print(f"\n👋 Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Example error: {e}")

if __name__ == "__main__":
    asyncio.run(main())