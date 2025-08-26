#!/usr/bin/env python3
"""
A2A wrapper for EKS AgentCore agent
"""

import asyncio
import json
from typing import Dict, Optional, Any, List
from datetime import datetime

# A2A imports
from a2a.types import (
    AgentCard, AgentCapabilities, AgentSkill, AgentProvider,
    Message, TextPart, Role
)

class EKSA2AWrapper:
    """A2A wrapper for EKS Agent"""
    
    def __init__(self, eks_agent_instance):
        self.eks_agent = eks_agent_instance
        self.agent_card = self._create_agent_card()
        self.clients: Dict[str, Any] = {}
        
        # Agent registry - in production, this would be dynamic discovery
        self.agent_registry = {
            "VPC-Agent": "https://vpc-agent.internal:8002",
            "Outposts-Agent": "https://outposts-agent.internal:8003", 
            "Prometheus-Agent": "https://prometheus-agent.internal:8004"
        }
    
    def _create_agent_card(self) -> AgentCard:
        """Create A2A agent card for EKS Agent"""
        
        capabilities = AgentCapabilities(
            streaming=True,
            push_notifications=False,
            state_transition_history=True,
            extensions=[]
        )
        
        skills = [
            AgentSkill(
                id="eks-cluster-management",
                name="cluster_management",
                description="Create, update, delete, and troubleshoot EKS clusters",
                tags=["kubernetes", "eks", "cluster", "management", "aws"]
            ),
            AgentSkill(
                id="eks-pod-diagnostics",
                name="pod_diagnostics", 
                description="Diagnose pod issues including logs, events, and resource usage",
                tags=["kubernetes", "pods", "diagnostics", "troubleshooting", "logs"]
            ),
            AgentSkill(
                id="eks-network-troubleshooting",
                name="network_troubleshooting",
                description="Troubleshoot EKS networking, connectivity, and DNS issues",
                tags=["networking", "connectivity", "dns", "troubleshooting", "vpc"]
            ),
            AgentSkill(
                id="eks-workload-management",
                name="workload_management",
                description="Manage Kubernetes workloads, deployments, and services",
                tags=["kubernetes", "workloads", "deployments", "services", "management"]
            ),
            AgentSkill(
                id="eks-security-analysis",
                name="security_analysis", 
                description="Analyze EKS security configurations and compliance",
                tags=["security", "compliance", "rbac", "policies", "analysis"]
            )
        ]
        
        provider = AgentProvider(
            organization="AWS Telco Infrastructure Team",
            url="https://aws.amazon.com/eks"
        )
        
        return AgentCard(
            name="EKS-Agent",
            version="1.0.0",
            description="AWS EKS management and troubleshooting agent built on Amazon Bedrock AgentCore. Provides comprehensive Kubernetes cluster management, pod diagnostics, network troubleshooting, and security analysis capabilities.",
            url="https://eks-agent.telco.internal:8001",
            capabilities=capabilities,
            skills=skills,
            provider=provider,
            default_input_modes=["text", "json"],
            default_output_modes=["text", "json", "yaml"],
            protocol_version="1.0"
        )
    
    async def send_request_to_agent(self, agent_name: str, request_data: Dict) -> Optional[Dict]:
        """Send A2A request to another agent"""
        
        agent_url = self.agent_registry.get(agent_name)
        if not agent_url:
            print(f"❌ Unknown agent: {agent_name}")
            return None
        
        try:
            # Create A2A message
            request_text = json.dumps(request_data, indent=2)
            message = Message(
                message_id=f"eks-req-{datetime.now().timestamp()}",
                role=Role.user,
                parts=[TextPart(text=request_text)],
                kind="message",
                context_id=f"eks-context-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )
            
            print(f"🔄 EKS Agent → {agent_name}")
            print(f"   Request: {request_data.get('action', 'unknown')}")
            
            # In production, this would use actual A2A client
            # client = await self.get_client(agent_url)
            # response = await client.send_message(message)
            
            # For now, simulate the response
            simulated_response = await self._simulate_agent_response(agent_name, request_data)
            
            return simulated_response
            
        except Exception as e:
            print(f"❌ A2A request to {agent_name} failed: {e}")
            return None
    
    async def _simulate_agent_response(self, agent_name: str, request_data: Dict) -> Dict:
        """Simulate responses from other agents for example purposes"""
        
        action = request_data.get('action', '')
        
        if agent_name == "VPC-Agent":
            if action == "analyze_network_connectivity":
                return {
                    "agent": "VPC-Agent",
                    "action": "analyze_network_connectivity",
                    "vpc_id": request_data.get('vpc_id'),
                    "analysis": {
                        "security_groups": {
                            "inbound_rules": ["Allow HTTPS (443) from 0.0.0.0/0", "Allow HTTP (80) from VPC"],
                            "outbound_rules": ["Allow all traffic to 0.0.0.0/0"],
                            "issues": ["Missing rule for Kubernetes API (6443)"]
                        },
                        "route_tables": {
                            "main_route": "0.0.0.0/0 → igw-123456",
                            "local_route": "10.0.0.0/16 → local",
                            "issues": []
                        },
                        "nacls": {
                            "status": "Default NACL allows all traffic",
                            "issues": []
                        },
                        "dns": {
                            "vpc_dns_resolution": True,
                            "vpc_dns_hostnames": True,
                            "issues": []
                        }
                    },
                    "recommendations": [
                        "Add security group rule for Kubernetes API port 6443",
                        "Consider restricting HTTP access to internal VPC only",
                        "Review outbound rules for least privilege access"
                    ],
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        elif agent_name == "Prometheus-Agent":
            if action == "get_cluster_metrics":
                return {
                    "agent": "Prometheus-Agent",
                    "action": "get_cluster_metrics",
                    "cluster_name": request_data.get('cluster_name'),
                    "timeframe": request_data.get('timeframe', '1h'),
                    "metrics": {
                        "cluster_health": {
                            "node_count": 3,
                            "nodes_ready": 3,
                            "pods_running": 45,
                            "pods_pending": 2,
                            "pods_failed": 1
                        },
                        "resource_usage": {
                            "cpu_utilization_avg": "65%",
                            "memory_utilization_avg": "72%",
                            "disk_utilization_avg": "45%"
                        },
                        "network_metrics": {
                            "network_errors": 3,
                            "dns_lookup_failures": 12,
                            "connection_timeouts": 5
                        },
                        "alerts": [
                            {"severity": "warning", "alert": "HighMemoryUsage", "node": "worker-node-2"},
                            {"severity": "critical", "alert": "DNSLookupFailures", "count": 12}
                        ]
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        elif agent_name == "Outposts-Agent":
            if action == "check_hybrid_connectivity":
                return {
                    "agent": "Outposts-Agent", 
                    "action": "check_hybrid_connectivity",
                    "outpost_id": request_data.get('outpost_id'),
                    "connectivity": {
                        "aws_region_connection": "healthy",
                        "local_gateway": "operational",
                        "bandwidth_utilization": "23%",
                        "latency_to_region": "15ms"
                    },
                    "hybrid_workloads": {
                        "eks_anywhere_clusters": 2,
                        "cross_region_services": ["RDS", "S3"],
                        "data_sync_status": "up_to_date"
                    },
                    "recommendations": [
                        "Monitor bandwidth usage during peak hours",
                        "Consider local caching for frequently accessed S3 objects"
                    ],
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # Default response
        return {
            "agent": agent_name,
            "action": action,
            "status": "processed",
            "message": f"Request processed by {agent_name}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_incoming_request(self, message: Message) -> Message:
        """Handle incoming A2A requests to EKS Agent"""
        
        try:
            # Parse the incoming request
            request_text = message.parts[0].text if message.parts else ""
            request_data = json.loads(request_text)
            
            # Route to appropriate EKS agent method
            response_data = await self._route_eks_request(request_data)
            
            # Create response message
            response = Message(
                message_id=f"eks-resp-{message.message_id}",
                role=Role.agent,
                parts=[TextPart(text=json.dumps(response_data, indent=2))],
                kind="message",
                context_id=message.context_id
            )
            
            return response
            
        except Exception as e:
            # Error response
            error_response = {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return Message(
                message_id=f"eks-error-{message.message_id}",
                role=Role.agent,
                parts=[TextPart(text=json.dumps(error_response, indent=2))],
                kind="message"
            )
    
    async def _route_eks_request(self, request_data: Dict) -> Dict:
        """Route incoming requests to appropriate EKS agent methods"""
        
        action = request_data.get('action', '')
        
        if action == "diagnose_pod":
            return await self._diagnose_pod_simulation(request_data)
        elif action == "analyze_cluster_health":
            return await self._analyze_cluster_health_simulation(request_data)
        elif action == "troubleshoot_networking":
            return await self._troubleshoot_networking_simulation(request_data)
        else:
            return {
                "status": "unknown_action",
                "message": f"EKS Agent doesn't support action: {action}",
                "supported_actions": ["diagnose_pod", "analyze_cluster_health", "troubleshoot_networking"]
            }
    
    async def _diagnose_pod_simulation(self, request_data: Dict) -> Dict:
        """Simulate pod diagnosis"""
        return {
            "action": "diagnose_pod",
            "pod_name": request_data.get('pod_name'),
            "namespace": request_data.get('namespace', 'default'),
            "diagnosis": {
                "status": "Running",
                "restart_count": 0,
                "ready": "1/1",
                "issues_detected": ["High memory usage", "DNS resolution delays"],
                "recommendations": ["Increase memory limits", "Check DNS configuration"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _analyze_cluster_health_simulation(self, request_data: Dict) -> Dict:
        """Simulate cluster health analysis"""
        return {
            "action": "analyze_cluster_health",
            "cluster_name": request_data.get('cluster_name'),
            "health_status": "degraded",
            "issues": [
                "2 nodes showing high memory pressure",
                "DNS lookup failures increasing",
                "Some pods in pending state"
            ],
            "recommendations": [
                "Scale cluster to add more nodes",
                "Investigate DNS configuration",
                "Check resource quotas"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _troubleshoot_networking_simulation(self, request_data: Dict) -> Dict:
        """Simulate network troubleshooting"""
        return {
            "action": "troubleshoot_networking",
            "cluster_name": request_data.get('cluster_name'),
            "network_analysis": {
                "cni_plugin": "aws-vpc-cni",
                "pod_networking": "functional",
                "service_discovery": "degraded",
                "ingress_connectivity": "healthy"
            },
            "issues": [
                "CoreDNS pods experiencing high latency",
                "Some service endpoints not updating"
            ],
            "needs_vpc_analysis": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Convenience methods for common cross-agent scenarios
    
    async def enhanced_pod_troubleshooting(self, pod_name: str, namespace: str = "default", cluster_name: str = None) -> Dict:
        """Enhanced pod troubleshooting with cross-agent collaboration"""
        
        print(f"🔍 Enhanced troubleshooting for pod {pod_name} in namespace {namespace}")
        
        # Step 1: Local EKS diagnosis
        pod_diagnosis = await self._diagnose_pod_simulation({
            "pod_name": pod_name,
            "namespace": namespace
        })
        
        results = {
            "pod_diagnosis": pod_diagnosis,
            "cross_agent_analysis": {}
        }
        
        # Step 2: Request metrics context from Prometheus Agent
        if cluster_name:
            print("📊 Requesting metrics context...")
            metrics_response = await self.send_request_to_agent("Prometheus-Agent", {
                "action": "get_cluster_metrics",
                "cluster_name": cluster_name,
                "timeframe": "1h"
            })
            
            if metrics_response:
                results["cross_agent_analysis"]["metrics"] = metrics_response
        
        # Step 3: If networking issues detected, request VPC analysis
        if pod_diagnosis.get("diagnosis", {}).get("issues_detected"):
            issues = pod_diagnosis["diagnosis"]["issues_detected"]
            if any("DNS" in issue or "network" in issue.lower() for issue in issues):
                print("🌐 Requesting VPC network analysis...")
                vpc_response = await self.send_request_to_agent("VPC-Agent", {
                    "action": "analyze_network_connectivity",
                    "vpc_id": "vpc-cluster-123",  # Would be dynamic in real implementation
                    "issue_description": f"Pod {pod_name} networking issues"
                })
                
                if vpc_response:
                    results["cross_agent_analysis"]["vpc_analysis"] = vpc_response
        
        # Step 4: Generate comprehensive recommendations
        results["comprehensive_recommendations"] = self._generate_comprehensive_recommendations(results)
        
        return results
    
    def _generate_comprehensive_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate comprehensive recommendations based on cross-agent analysis"""
        
        recommendations = []
        
        # Add pod-specific recommendations
        pod_recs = analysis_results.get("pod_diagnosis", {}).get("diagnosis", {}).get("recommendations", [])
        recommendations.extend(pod_recs)
        
        # Add VPC-specific recommendations
        vpc_recs = analysis_results.get("cross_agent_analysis", {}).get("vpc_analysis", {}).get("recommendations", [])
        recommendations.extend(vpc_recs)
        
        # Add metrics-based recommendations
        metrics = analysis_results.get("cross_agent_analysis", {}).get("metrics", {})
        if metrics:
            alerts = metrics.get("metrics", {}).get("alerts", [])
            for alert in alerts:
                if alert.get("severity") == "critical":
                    recommendations.append(f"URGENT: Address {alert.get('alert')} alert")
        
        # Add cross-cutting recommendations
        recommendations.extend([
            "Monitor pod performance over next 24 hours",
            "Consider implementing pod disruption budgets",
            "Review resource requests and limits"
        ])
        
        return list(set(recommendations))  # Remove duplicates