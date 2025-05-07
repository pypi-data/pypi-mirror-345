"""
Kubernetes monitoring module.

This module provides functionality for monitoring Kubernetes clusters,
including resource utilization, health checks, and event monitoring.
"""

import os
import json
import logging
import time
import re
from typing import Dict, Any, List, Optional, Tuple
import subprocess
from datetime import datetime, timedelta
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class KubernetesMonitoring:
    """Kubernetes monitoring operations."""
    
    def __init__(self):
        """Initialize Kubernetes client."""
        try:
            config.load_kube_config()
            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.metrics_v1beta1 = None
            
            try:
                self.metrics_v1beta1 = client.CustomObjectsApi()
            except Exception as e:
                logger.warning(f"Metrics API not available: {e}")
                
            self.history = {}
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise

    def run_command(self, cmd: List[str]) -> str:
        """Run a kubectl command and return the output."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(cmd)}")
            logger.error(f"Error output: {e.stderr}")
            return f"Error: {e.stderr}"

    def check_cluster_health(self) -> Dict[str, Any]:
        """Check overall cluster health."""
        try:
            nodes = self.core_v1.list_node()
            node_status = {
                "total": len(nodes.items),
                "ready": 0,
                "not_ready": 0,
                "details": []
            }
            
            for node in nodes.items:
                is_ready = False
                for condition in node.status.conditions or []:
                    if condition.type == "Ready":
                        is_ready = condition.status == "True"
                        break
                
                if is_ready:
                    node_status["ready"] += 1
                else:
                    node_status["not_ready"] += 1
                    
                node_status["details"].append({
                    "name": node.metadata.name,
                    "status": "Ready" if is_ready else "NotReady",
                    "conditions": [
                        {
                            "type": condition.type,
                            "status": condition.status,
                            "message": condition.message
                        } for condition in node.status.conditions or []
                    ]
                })
            
            control_plane_status = self._check_control_plane_components()
            
            overall_status = "Healthy"
            if node_status["not_ready"] > 0 or not control_plane_status["healthy"]:
                overall_status = "Unhealthy"
            
            return {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "nodes": node_status,
                "control_plane": control_plane_status,
                "api_server": self._check_api_server_health()
            }
        except Exception as e:
            logger.error(f"Failed to check cluster health: {e}")
            return {
                "status": "Error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _check_control_plane_components(self) -> Dict[str, Any]:
        """Check health of control plane components."""
        try:
            cmd = ["kubectl", "get", "componentstatuses", "-o", "json"]
            result = self.run_command(cmd)
            
            if result.startswith("Error"):
                return {
                    "healthy": False,
                    "error": result,
                    "components": []
                }
            
            try:
                data = json.loads(result)
                components = []
                all_healthy = True
                
                for item in data.get("items", []):
                    component_name = item.get("metadata", {}).get("name", "unknown")
                    conditions = item.get("conditions", [])
                    
                    is_healthy = False
                    for condition in conditions:
                        if condition.get("type") == "Healthy" and condition.get("status") == "True":
                            is_healthy = True
                            break
                    
                    if not is_healthy:
                        all_healthy = False
                        
                    components.append({
                        "name": component_name,
                        "healthy": is_healthy,
                        "message": conditions[0].get("message") if conditions else "No status"
                    })
                
                return {
                    "healthy": all_healthy,
                    "components": components
                }
            except json.JSONDecodeError:
                return {
                    "healthy": "Unhealthy" not in result,
                    "components": [{"name": "control-plane", "message": result}]
                }
        except Exception as e:
            logger.error(f"Failed to check control plane components: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "components": []
            }

    def _check_api_server_health(self) -> Dict[str, Any]:
        """Check Kubernetes API server health."""
        try:
            self.core_v1.get_api_resources()
            return {
                "status": "Healthy",
                "response_time_ms": 0  # Would need timing logic to measure
            }
        except Exception as e:
            logger.error(f"API server health check failed: {e}")
            return {
                "status": "Unhealthy",
                "error": str(e)
            }

    def get_resource_utilization(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get resource utilization for nodes and pods."""
        try:
            node_metrics = self._get_node_metrics()
            
            pod_metrics = self._get_pod_metrics(namespace)
            
            timestamp = datetime.now().isoformat()
            if "metrics" not in self.history:
                self.history["metrics"] = []
                
            if len(self.history["metrics"]) >= 100:
                self.history["metrics"].pop(0)
                
            self.history["metrics"].append({
                "timestamp": timestamp,
                "nodes": node_metrics,
                "pods": pod_metrics
            })
            
            return {
                "timestamp": timestamp,
                "nodes": node_metrics,
                "pods": pod_metrics
            }
        except Exception as e:
            logger.error(f"Failed to get resource utilization: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _get_node_metrics(self) -> List[Dict[str, Any]]:
        """Get node resource metrics."""
        try:
            cmd = ["kubectl", "top", "nodes", "--no-headers"]
            result = self.run_command(cmd)
            
            if result.startswith("Error"):
                logger.warning(f"Failed to get node metrics: {result}")
                return []
            
            metrics = []
            for line in result.strip().split('\n'):
                if not line.strip():
                    continue
                    
                parts = line.split()
                if len(parts) >= 5:
                    node_name = parts[0]
                    cpu_usage = parts[1]
                    cpu_percent = parts[2]
                    memory_usage = parts[3]
                    memory_percent = parts[4]
                    
                    metrics.append({
                        "name": node_name,
                        "cpu": {
                            "usage": cpu_usage,
                            "percent": cpu_percent
                        },
                        "memory": {
                            "usage": memory_usage,
                            "percent": memory_percent
                        }
                    })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting node metrics: {e}")
            return []

    def _get_pod_metrics(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pod resource metrics."""
        try:
            cmd = ["kubectl", "top", "pods"]
            if namespace:
                cmd.extend(["-n", namespace])
            cmd.append("--no-headers")
            
            result = self.run_command(cmd)
            
            if result.startswith("Error"):
                logger.warning(f"Failed to get pod metrics: {result}")
                return []
            
            metrics = []
            for line in result.strip().split('\n'):
                if not line.strip():
                    continue
                    
                parts = line.split()
                if len(parts) >= 3:
                    pod_name = parts[0]
                    cpu_usage = parts[1]
                    memory_usage = parts[2]
                    
                    metrics.append({
                        "name": pod_name,
                        "namespace": namespace or "default",
                        "cpu": cpu_usage,
                        "memory": memory_usage
                    })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting pod metrics: {e}")
            return []

    def check_pod_health(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Check health status of pods."""
        try:
            if namespace:
                pods = self.core_v1.list_namespaced_pod(namespace=namespace)
            else:
                pods = self.core_v1.list_pod_for_all_namespaces()
            
            results = []
            for pod in pods.items:
                phase = pod.status.phase
                
                containers = []
                for container_status in pod.status.container_statuses or []:
                    container_health = {
                        "name": container_status.name,
                        "ready": container_status.ready,
                        "restart_count": container_status.restart_count,
                        "state": "unknown"
                    }
                    
                    if container_status.state.running:
                        container_health["state"] = "running"
                    elif container_status.state.waiting:
                        container_health["state"] = "waiting"
                        container_health["reason"] = container_status.state.waiting.reason
                        container_health["message"] = container_status.state.waiting.message
                    elif container_status.state.terminated:
                        container_health["state"] = "terminated"
                        container_health["reason"] = container_status.state.terminated.reason
                        container_health["exit_code"] = container_status.state.terminated.exit_code
                    
                    for container in pod.spec.containers:
                        if container.name == container_status.name:
                            container_health["has_readiness_probe"] = container.readiness_probe is not None
                            container_health["has_liveness_probe"] = container.liveness_probe is not None
                            container_health["has_startup_probe"] = container.startup_probe is not None
                            break
                    
                    containers.append(container_health)
                
                is_healthy = phase == "Running" and all(c["ready"] for c in containers)
                
                conditions = []
                for condition in pod.status.conditions or []:
                    conditions.append({
                        "type": condition.type,
                        "status": condition.status,
                        "reason": condition.reason,
                        "message": condition.message,
                        "last_transition_time": condition.last_transition_time.isoformat() if condition.last_transition_time else None
                    })
                
                results.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "phase": phase,
                    "healthy": is_healthy,
                    "containers": containers,
                    "conditions": conditions,
                    "node": pod.spec.node_name,
                    "ip": pod.status.pod_ip,
                    "creation_time": pod.metadata.creation_timestamp.isoformat() if pod.metadata.creation_timestamp else None
                })
            
            return {
                "timestamp": datetime.now().isoformat(),
                "pods": results,
                "count": len(results),
                "healthy_count": sum(1 for pod in results if pod["healthy"]),
                "unhealthy_count": sum(1 for pod in results if not pod["healthy"])
            }
        except Exception as e:
            logger.error(f"Failed to check pod health: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "pods": []
            }

    def monitor_events(self, namespace: Optional[str] = None, 
                      types: Optional[List[str]] = None,
                      since: Optional[int] = None) -> Dict[str, Any]:
        """Monitor Kubernetes events."""
        try:
            if namespace:
                events = self.core_v1.list_namespaced_event(namespace=namespace)
            else:
                events = self.core_v1.list_event_for_all_namespaces()
            
            filtered_events = []
            now = datetime.now(events.items[0].last_timestamp.tzinfo if events.items else None)
            
            for event in events.items:
                if types and event.type not in types:
                    continue
                
                if since and event.last_timestamp:
                    age = now - event.last_timestamp
                    if age > timedelta(minutes=since):
                        continue
                
                filtered_events.append({
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "count": event.count,
                    "object": f"{event.involved_object.kind}/{event.involved_object.name}",
                    "namespace": event.involved_object.namespace,
                    "first_timestamp": event.first_timestamp.isoformat() if event.first_timestamp else None,
                    "last_timestamp": event.last_timestamp.isoformat() if event.last_timestamp else None,
                    "source": event.source.component if event.source else None
                })
            
            filtered_events.sort(key=lambda e: e["last_timestamp"] if e["last_timestamp"] else "", reverse=True)
            
            alerts = []
            for event in filtered_events:
                if event["type"] == "Warning":
                    alerts.append({
                        "level": "warning",
                        "message": f"{event['reason']}: {event['message']}",
                        "object": event["object"],
                        "namespace": event["namespace"],
                        "timestamp": event["last_timestamp"]
                    })
            
            return {
                "timestamp": datetime.now().isoformat(),
                "events": filtered_events,
                "count": len(filtered_events),
                "alerts": alerts,
                "alert_count": len(alerts)
            }
        except Exception as e:
            logger.error(f"Failed to monitor events: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "events": [],
                "alerts": []
            }

    def analyze_node_capacity(self) -> Dict[str, Any]:
        """Analyze node capacity and resource allocation."""
        try:
            nodes = self.core_v1.list_node()
            
            node_metrics = self._get_node_metrics()
            metrics_by_name = {m["name"]: m for m in node_metrics}
            
            results = []
            for node in nodes.items:
                node_name = node.metadata.name
                
                capacity = node.status.capacity
                allocatable = node.status.allocatable
                
                usage = {"cpu": "N/A", "memory": "N/A"}
                if node_name in metrics_by_name:
                    usage = {
                        "cpu": metrics_by_name[node_name]["cpu"]["usage"],
                        "memory": metrics_by_name[node_name]["memory"]["usage"]
                    }
                
                field_selector = f"spec.nodeName={node_name},status.phase!=Failed,status.phase!=Succeeded"
                pods = self.core_v1.list_pod_for_all_namespaces(field_selector=field_selector)
                
                allocated = {"cpu": 0, "memory": 0}
                for pod in pods.items:
                    for container in pod.spec.containers:
                        if container.resources and container.resources.requests:
                            cpu_request = container.resources.requests.get("cpu", "0")
                            memory_request = container.resources.requests.get("memory", "0")
                            
                            if isinstance(cpu_request, str):
                                if cpu_request.endswith("m"):
                                    allocated["cpu"] += int(cpu_request[:-1])
                                else:
                                    try:
                                        allocated["cpu"] += int(float(cpu_request) * 1000)
                                    except ValueError:
                                        pass
                            
                            if isinstance(memory_request, str):
                                try:
                                    if memory_request.endswith("Ki"):
                                        allocated["memory"] += int(memory_request[:-2]) * 1024
                                    elif memory_request.endswith("Mi"):
                                        allocated["memory"] += int(memory_request[:-2]) * 1024 * 1024
                                    elif memory_request.endswith("Gi"):
                                        allocated["memory"] += int(memory_request[:-2]) * 1024 * 1024 * 1024
                                    else:
                                        allocated["memory"] += int(memory_request)
                                except ValueError:
                                    pass
                
                allocated_formatted = {
                    "cpu": f"{allocated['cpu']}m",
                    "memory": self._format_bytes(allocated["memory"])
                }
                
                conditions = []
                for condition in node.status.conditions or []:
                    conditions.append({
                        "type": condition.type,
                        "status": condition.status,
                        "reason": condition.reason,
                        "message": condition.message,
                        "last_transition_time": condition.last_transition_time.isoformat() if condition.last_transition_time else None
                    })
                
                results.append({
                    "name": node_name,
                    "capacity": {
                        "cpu": capacity.get("cpu", "N/A"),
                        "memory": capacity.get("memory", "N/A"),
                        "pods": capacity.get("pods", "N/A")
                    },
                    "allocatable": {
                        "cpu": allocatable.get("cpu", "N/A"),
                        "memory": allocatable.get("memory", "N/A"),
                        "pods": allocatable.get("pods", "N/A")
                    },
                    "allocated": allocated_formatted,
                    "usage": usage,
                    "conditions": conditions,
                    "labels": node.metadata.labels,
                    "taints": [
                        {
                            "key": taint.key,
                            "value": taint.value,
                            "effect": taint.effect
                        } for taint in (node.spec.taints or [])
                    ]
                })
            
            return {
                "timestamp": datetime.now().isoformat(),
                "nodes": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Failed to analyze node capacity: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "nodes": []
            }

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human-readable string."""
        if bytes_value < 1024:
            return f"{bytes_value}B"
        elif bytes_value < 1024 * 1024:
            return f"{bytes_value / 1024:.2f}Ki"
        elif bytes_value < 1024 * 1024 * 1024:
            return f"{bytes_value / (1024 * 1024):.2f}Mi"
        else:
            return f"{bytes_value / (1024 * 1024 * 1024):.2f}Gi"

    def get_historical_metrics(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """Get historical metrics for the specified duration."""
        try:
            if "metrics" not in self.history:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "message": "No historical data available",
                    "data": []
                }
            
            cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
            filtered_metrics = []
            
            for entry in self.history["metrics"]:
                try:
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if entry_time >= cutoff_time:
                        filtered_metrics.append(entry)
                except (ValueError, TypeError):
                    continue
            
            return {
                "timestamp": datetime.now().isoformat(),
                "duration_minutes": duration_minutes,
                "data_points": len(filtered_metrics),
                "data": filtered_metrics
            }
        except Exception as e:
            logger.error(f"Failed to get historical metrics: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "data": []
            }

    def track_container_health(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Track container readiness and liveness."""
        try:
            if namespace:
                pods = self.core_v1.list_namespaced_pod(namespace=namespace)
            else:
                pods = self.core_v1.list_pod_for_all_namespaces()
            
            results = []
            for pod in pods.items:
                containers = []
                
                for container in pod.spec.containers:
                    status = None
                    for cs in pod.status.container_statuses or []:
                        if cs.name == container.name:
                            status = cs
                            break
                    
                    readiness_probe = None
                    if container.readiness_probe:
                        readiness_probe = {
                            "initial_delay_seconds": container.readiness_probe.initial_delay_seconds,
                            "timeout_seconds": container.readiness_probe.timeout_seconds,
                            "period_seconds": container.readiness_probe.period_seconds,
                            "success_threshold": container.readiness_probe.success_threshold,
                            "failure_threshold": container.readiness_probe.failure_threshold,
                            "type": self._get_probe_type(container.readiness_probe)
                        }
                    
                    liveness_probe = None
                    if container.liveness_probe:
                        liveness_probe = {
                            "initial_delay_seconds": container.liveness_probe.initial_delay_seconds,
                            "timeout_seconds": container.liveness_probe.timeout_seconds,
                            "period_seconds": container.liveness_probe.period_seconds,
                            "success_threshold": container.liveness_probe.success_threshold,
                            "failure_threshold": container.liveness_probe.failure_threshold,
                            "type": self._get_probe_type(container.liveness_probe)
                        }
                    
                    startup_probe = None
                    if container.startup_probe:
                        startup_probe = {
                            "initial_delay_seconds": container.startup_probe.initial_delay_seconds,
                            "timeout_seconds": container.startup_probe.timeout_seconds,
                            "period_seconds": container.startup_probe.period_seconds,
                            "success_threshold": container.startup_probe.success_threshold,
                            "failure_threshold": container.startup_probe.failure_threshold,
                            "type": self._get_probe_type(container.startup_probe)
                        }
                    
                    container_info = {
                        "name": container.name,
                        "image": container.image,
                        "ready": status.ready if status else False,
                        "restart_count": status.restart_count if status else 0,
                        "state": self._get_container_state(status) if status else "unknown",
                        "readiness_probe": readiness_probe,
                        "liveness_probe": liveness_probe,
                        "startup_probe": startup_probe
                    }
                    
                    containers.append(container_info)
                
                results.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "phase": pod.status.phase,
                    "containers": containers
                })
            
            return {
                "timestamp": datetime.now().isoformat(),
                "pods": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Failed to track container health: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "pods": []
            }

    def _get_probe_type(self, probe) -> str:
        """Determine the type of probe (HTTP, TCP, Exec)."""
        if probe.http_get:
            return "http"
        elif probe.tcp_socket:
            return "tcp"
        elif probe.exec:
            return "exec"
        else:
            return "unknown"

    def _get_container_state(self, container_status) -> Dict[str, Any]:
        """Get container state details."""
        if container_status.state.running:
            return {
                "type": "running",
                "started_at": container_status.state.running.started_at.isoformat() if container_status.state.running.started_at else None
            }
        elif container_status.state.waiting:
            return {
                "type": "waiting",
                "reason": container_status.state.waiting.reason,
                "message": container_status.state.waiting.message
            }
        elif container_status.state.terminated:
            return {
                "type": "terminated",
                "reason": container_status.state.terminated.reason,
                "exit_code": container_status.state.terminated.exit_code,
                "started_at": container_status.state.terminated.started_at.isoformat() if container_status.state.terminated.started_at else None,
                "finished_at": container_status.state.terminated.finished_at.isoformat() if container_status.state.terminated.finished_at else None
            }
        else:
            return {"type": "unknown"}
