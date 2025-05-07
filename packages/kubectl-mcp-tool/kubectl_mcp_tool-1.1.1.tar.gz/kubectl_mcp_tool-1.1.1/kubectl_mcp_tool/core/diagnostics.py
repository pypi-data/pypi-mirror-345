"""
Kubernetes diagnostics module.

This module provides functionality for diagnosing issues in Kubernetes clusters,
including configuration validation, error analysis, and troubleshooting.
"""

import os
import json
import logging
import re
import yaml
from typing import Dict, Any, List, Optional, Tuple
import subprocess
from datetime import datetime, timedelta
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class KubernetesDiagnostics:
    """Kubernetes diagnostics operations."""
    
    def __init__(self):
        """Initialize Kubernetes client."""
        try:
            config.load_kube_config()
            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.networking_v1 = client.NetworkingV1Api()
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

    def diagnose_cluster(self) -> Dict[str, Any]:
        """Run a comprehensive cluster diagnostic."""
        try:
            results = {
                "timestamp": datetime.now().isoformat(),
                "connection_status": self._check_connection(),
                "api_server_status": self._check_api_server(),
                "node_status": self._check_nodes(),
                "control_plane_status": self._check_control_plane(),
                "resource_issues": self._check_resource_issues(),
                "pod_issues": self._check_pod_issues(),
                "networking_issues": self._check_networking_issues()
            }
            
            if (results["connection_status"]["status"] == "ok" and
                results["api_server_status"]["status"] == "ok" and
                results["node_status"]["status"] == "ok" and
                results["control_plane_status"]["status"] == "ok"):
                results["overall_status"] = "healthy"
            else:
                results["overall_status"] = "unhealthy"
                
            return results
        except Exception as e:
            logger.error(f"Failed to diagnose cluster: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }

    def _check_connection(self) -> Dict[str, Any]:
        """Check connection to the Kubernetes cluster."""
        try:
            cmd = ["kubectl", "version", "--short"]
            result = self.run_command(cmd)
            
            if result.startswith("Error"):
                return {
                    "status": "error",
                    "message": "Failed to connect to Kubernetes cluster",
                    "details": result
                }
            
            return {
                "status": "ok",
                "message": "Successfully connected to Kubernetes cluster",
                "version_info": result
            }
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return {
                "status": "error",
                "message": f"Connection check failed: {str(e)}"
            }

    def _check_api_server(self) -> Dict[str, Any]:
        """Check Kubernetes API server health."""
        try:
            cmd = ["kubectl", "get", "--raw", "/healthz"]
            result = self.run_command(cmd)
            
            if result != "ok" and not result.startswith("Error"):
                return {
                    "status": "warning",
                    "message": "API server health check returned unexpected response",
                    "details": result
                }
            elif result.startswith("Error"):
                return {
                    "status": "error",
                    "message": "API server health check failed",
                    "details": result
                }
            
            return {
                "status": "ok",
                "message": "API server is healthy"
            }
        except Exception as e:
            logger.error(f"API server check failed: {e}")
            return {
                "status": "error",
                "message": f"API server check failed: {str(e)}"
            }

    def _check_nodes(self) -> Dict[str, Any]:
        """Check node status in the cluster."""
        try:
            nodes = self.core_v1.list_node()
            
            node_statuses = []
            not_ready_count = 0
            
            for node in nodes.items:
                node_status = {
                    "name": node.metadata.name,
                    "status": "NotReady",
                    "conditions": []
                }
                
                for condition in node.status.conditions or []:
                    node_status["conditions"].append({
                        "type": condition.type,
                        "status": condition.status,
                        "message": condition.message
                    })
                    
                    if condition.type == "Ready" and condition.status == "True":
                        node_status["status"] = "Ready"
                
                if node_status["status"] == "NotReady":
                    not_ready_count += 1
                    
                node_statuses.append(node_status)
            
            status = "ok" if not_ready_count == 0 else "error"
            message = "All nodes are ready" if not_ready_count == 0 else f"{not_ready_count} nodes are not ready"
            
            return {
                "status": status,
                "message": message,
                "nodes": node_statuses,
                "total_nodes": len(node_statuses),
                "not_ready_count": not_ready_count
            }
        except Exception as e:
            logger.error(f"Node check failed: {e}")
            return {
                "status": "error",
                "message": f"Node check failed: {str(e)}"
            }

    def _check_control_plane(self) -> Dict[str, Any]:
        """Check control plane components."""
        try:
            cmd = ["kubectl", "get", "componentstatuses", "-o", "json"]
            result = self.run_command(cmd)
            
            if result.startswith("Error"):
                return self._check_control_plane_pods()
            
            try:
                data = json.loads(result)
                components = []
                unhealthy_count = 0
                
                for item in data.get("items", []):
                    component_name = item.get("metadata", {}).get("name", "unknown")
                    conditions = item.get("conditions", [])
                    
                    is_healthy = False
                    message = "No status"
                    
                    for condition in conditions:
                        if condition.get("type") == "Healthy":
                            is_healthy = condition.get("status") == "True"
                            message = condition.get("message", "")
                            break
                    
                    if not is_healthy:
                        unhealthy_count += 1
                        
                    components.append({
                        "name": component_name,
                        "healthy": is_healthy,
                        "message": message
                    })
                
                status = "ok" if unhealthy_count == 0 else "error"
                message = "All control plane components are healthy" if unhealthy_count == 0 else f"{unhealthy_count} control plane components are unhealthy"
                
                return {
                    "status": status,
                    "message": message,
                    "components": components,
                    "total_components": len(components),
                    "unhealthy_count": unhealthy_count
                }
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "message": "Failed to parse control plane status",
                    "details": result
                }
        except Exception as e:
            logger.error(f"Control plane check failed: {e}")
            return {
                "status": "error",
                "message": f"Control plane check failed: {str(e)}"
            }

    def _check_control_plane_pods(self) -> Dict[str, Any]:
        """Check control plane pods in kube-system namespace."""
        try:
            pods = self.core_v1.list_namespaced_pod(namespace="kube-system")
            
            control_plane_pods = []
            unhealthy_count = 0
            
            control_plane_components = [
                "kube-apiserver", "kube-controller-manager", "kube-scheduler", "etcd"
            ]
            
            for pod in pods.items:
                for component in control_plane_components:
                    if component in pod.metadata.name:
                        is_healthy = pod.status.phase == "Running"
                        
                        if not is_healthy:
                            unhealthy_count += 1
                            
                        control_plane_pods.append({
                            "name": pod.metadata.name,
                            "healthy": is_healthy,
                            "status": pod.status.phase,
                            "message": f"Pod is {pod.status.phase}"
                        })
            
            if not control_plane_pods:
                return {
                    "status": "ok",
                    "message": "No control plane pods found, possibly running on managed Kubernetes",
                    "components": []
                }
            
            status = "ok" if unhealthy_count == 0 else "error"
            message = "All control plane pods are healthy" if unhealthy_count == 0 else f"{unhealthy_count} control plane pods are unhealthy"
            
            return {
                "status": status,
                "message": message,
                "components": control_plane_pods,
                "total_components": len(control_plane_pods),
                "unhealthy_count": unhealthy_count
            }
        except Exception as e:
            logger.error(f"Control plane pods check failed: {e}")
            return {
                "status": "error",
                "message": f"Control plane pods check failed: {str(e)}"
            }

    def _check_resource_issues(self) -> Dict[str, Any]:
        """Check for resource constraint issues."""
        try:
            nodes = self.core_v1.list_node()
            
            resource_issues = []
            
            for node in nodes.items:
                node_name = node.metadata.name
                
                for condition in node.status.conditions or []:
                    if condition.type in ["MemoryPressure", "DiskPressure", "PIDPressure"] and condition.status == "True":
                        resource_issues.append({
                            "type": "node_pressure",
                            "node": node_name,
                            "condition": condition.type,
                            "message": condition.message
                        })
            
            pods = self.core_v1.list_pod_for_all_namespaces()
            
            for pod in pods.items:
                if pod.status.phase != "Running":
                    continue
                    
                for container_status in pod.status.container_statuses or []:
                    if container_status.restart_count > 5:
                        resource_issues.append({
                            "type": "container_restarts",
                            "pod": pod.metadata.name,
                            "namespace": pod.metadata.namespace,
                            "container": container_status.name,
                            "restart_count": container_status.restart_count,
                            "message": f"Container has restarted {container_status.restart_count} times, possible resource constraints"
                        })
                    
                    if container_status.state.waiting and container_status.state.waiting.reason in ["CrashLoopBackOff", "OOMKilled"]:
                        resource_issues.append({
                            "type": "container_crash",
                            "pod": pod.metadata.name,
                            "namespace": pod.metadata.namespace,
                            "container": container_status.name,
                            "reason": container_status.state.waiting.reason,
                            "message": container_status.state.waiting.message
                        })
            
            return {
                "issues": resource_issues,
                "count": len(resource_issues)
            }
        except Exception as e:
            logger.error(f"Resource issues check failed: {e}")
            return {
                "error": str(e),
                "issues": [],
                "count": 0
            }

    def _check_pod_issues(self) -> Dict[str, Any]:
        """Check for pod-related issues."""
        try:
            pods = self.core_v1.list_pod_for_all_namespaces()
            
            pod_issues = []
            
            for pod in pods.items:
                if pod.status.phase not in ["Running", "Succeeded"]:
                    pod_issues.append({
                        "type": "pod_not_running",
                        "pod": pod.metadata.name,
                        "namespace": pod.metadata.namespace,
                        "phase": pod.status.phase,
                        "message": f"Pod is in {pod.status.phase} phase"
                    })
                
                for container_status in pod.status.container_statuses or []:
                    if not container_status.ready and pod.status.phase == "Running":
                        reason = "Unknown"
                        message = "Container is not ready"
                        
                        if container_status.state.waiting:
                            reason = container_status.state.waiting.reason
                            message = container_status.state.waiting.message
                        elif container_status.state.terminated:
                            reason = container_status.state.terminated.reason
                            message = f"Container terminated with exit code {container_status.state.terminated.exit_code}"
                        
                        pod_issues.append({
                            "type": "container_not_ready",
                            "pod": pod.metadata.name,
                            "namespace": pod.metadata.namespace,
                            "container": container_status.name,
                            "reason": reason,
                            "message": message
                        })
            
            return {
                "issues": pod_issues,
                "count": len(pod_issues)
            }
        except Exception as e:
            logger.error(f"Pod issues check failed: {e}")
            return {
                "error": str(e),
                "issues": [],
                "count": 0
            }

    def _check_networking_issues(self) -> Dict[str, Any]:
        """Check for networking-related issues."""
        try:
            services = self.core_v1.list_service_for_all_namespaces()
            
            networking_issues = []
            
            for service in services.items:
                try:
                    endpoints = self.core_v1.read_namespaced_endpoints(
                        name=service.metadata.name,
                        namespace=service.metadata.namespace
                    )
                    
                    if not endpoints.subsets or not any(subset.addresses for subset in endpoints.subsets):
                        networking_issues.append({
                            "type": "service_without_endpoints",
                            "service": service.metadata.name,
                            "namespace": service.metadata.namespace,
                            "selector": service.spec.selector,
                            "message": "Service has no endpoints"
                        })
                except ApiException:
                    networking_issues.append({
                        "type": "missing_endpoints",
                        "service": service.metadata.name,
                        "namespace": service.metadata.namespace,
                        "message": "Endpoints object not found for service"
                    })
            
            return {
                "issues": networking_issues,
                "count": len(networking_issues)
            }
        except Exception as e:
            logger.error(f"Networking issues check failed: {e}")
            return {
                "error": str(e),
                "issues": [],
                "count": 0
            }

    def analyze_logs(self, pod_name: str, container: Optional[str] = None, 
                    namespace: str = "default", tail: int = 100) -> Dict[str, Any]:
        """Analyze logs from a pod for common error patterns."""
        try:
            cmd = ["kubectl", "logs", pod_name, "-n", namespace, f"--tail={tail}"]
            if container:
                cmd.extend(["-c", container])
            
            logs = self.run_command(cmd)
            
            if logs.startswith("Error"):
                return {
                    "status": "error",
                    "message": "Failed to retrieve logs",
                    "details": logs
                }
            
            error_patterns = {
                "oom_killed": r"(Out of memory|OOMKilled|Killed|signal: 9)",
                "connection_refused": r"(connection refused|cannot connect|dial tcp|connection reset)",
                "permission_denied": r"(permission denied|unauthorized|access denied|forbidden)",
                "not_found": r"(not found|404|no such file|doesn't exist)",
                "timeout": r"(timeout|timed out|deadline exceeded)",
                "crash_loop": r"(back-off|CrashLoopBackOff|restarting failed container)",
                "config_error": r"(invalid config|configuration error|ConfigMap.*not found|Secret.*not found)",
                "api_error": r"(API server|status code 5\d\d|internal server error)"
            }
            
            errors_found = {}
            for error_type, pattern in error_patterns.items():
                matches = re.findall(pattern, logs, re.IGNORECASE)
                if matches:
                    errors_found[error_type] = len(matches)
            
            suggestions = []
            if "oom_killed" in errors_found:
                suggestions.append("Increase memory limits for the container")
            if "connection_refused" in errors_found:
                suggestions.append("Check network connectivity and service endpoints")
            if "permission_denied" in errors_found:
                suggestions.append("Verify RBAC permissions and service account configuration")
            
            return {
                "status": "success",
                "pod": pod_name,
                "container": container,
                "namespace": namespace,
                "log_lines": logs.count('\n') + 1 if logs else 0,
                "has_errors": bool(errors_found),
                "errors_found": errors_found,
                "error_count": sum(errors_found.values()),
                "suggestions": suggestions
            }
        except Exception as e:
            logger.error(f"Log analysis failed: {e}")
            return {
                "status": "error",
                "message": f"Log analysis failed: {str(e)}"
            }

    def validate_configuration(self, yaml_content: str) -> Dict[str, Any]:
        """Validate Kubernetes YAML configuration."""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
                f.write(yaml_content)
                temp_file = f.name
            
            cmd = ["kubectl", "apply", "--dry-run=client", "-f", temp_file]
            result = self.run_command(cmd)
            
            os.unlink(temp_file)
            
            if result.startswith("Error"):
                return {
                    "valid": False,
                    "message": "Configuration validation failed",
                    "errors": [result]
                }
            
            return {
                "valid": True,
                "message": "Configuration is valid"
            }
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return {
                "valid": False,
                "message": f"Validation failed: {str(e)}",
                "errors": [str(e)]
            }
