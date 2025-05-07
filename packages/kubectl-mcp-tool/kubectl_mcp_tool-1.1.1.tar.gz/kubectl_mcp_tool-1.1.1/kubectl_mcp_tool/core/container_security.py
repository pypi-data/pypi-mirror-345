import logging
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from kubernetes import client
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class KubernetesContainerSecurity:
    """Class for container security scanning and best practices enforcement."""
    
    def __init__(self, api_client=None):
        """Initialize the KubernetesContainerSecurity class."""
        self.api_client = api_client or client.ApiClient()
        self.core_v1 = client.CoreV1Api(self.api_client)
    
    def run_command(self, cmd: List[str]) -> str:
        """Run a command and return the output."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(cmd)}")
            logger.error(f"Error: {e.stderr}")
            raise RuntimeError(f"Command failed: {e.stderr}")
    
    def scan_container_images(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Scan container images for vulnerabilities using Trivy if available."""
        try:
            try:
                self.run_command(["trivy", "--version"])
                trivy_available = True
            except Exception:
                trivy_available = False
                logger.warning("Trivy not found. Container scanning will be limited.")
            
            if namespace:
                pods = self.core_v1.list_namespaced_pod(namespace=namespace)
            else:
                pods = self.core_v1.list_pod_for_all_namespaces()
            
            results = []
            
            for pod in pods.items:
                pod_data = {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "containers": []
                }
                
                for container in pod.spec.containers:
                    container_data = {
                        "name": container.name,
                        "image": container.image,
                        "scan_results": None
                    }
                    
                    if trivy_available:
                        try:
                            scan_output = self.run_command(["trivy", "image", "--quiet", "--format", "json", container.image])
                            container_data["scan_results"] = {
                                "raw_output": scan_output,
                                "status": "success"
                            }
                        except Exception as e:
                            container_data["scan_results"] = {
                                "status": "error",
                                "error": str(e)
                            }
                    
                    pod_data["containers"].append(container_data)
                
                results.append(pod_data)
            
            return {
                "status": "success",
                "trivy_available": trivy_available,
                "pod_count": len(results),
                "container_count": sum(len(pod["containers"]) for pod in results),
                "scan_results": results
            }
        except ApiException as e:
            return {
                "status": "error",
                "error": f"Failed to scan container images: {e.reason}",
                "details": e.body
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to scan container images: {str(e)}"
            }
    
    def enforce_security_best_practices(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Enforce security best practices by checking for common issues."""
        try:
            if namespace:
                pods = self.core_v1.list_namespaced_pod(namespace=namespace)
            else:
                pods = self.core_v1.list_pod_for_all_namespaces()
            
            results = []
            
            for pod in pods.items:
                pod_data = {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "issues": []
                }
                
                if not pod.spec.security_context:
                    pod_data["issues"].append({
                        "severity": "medium",
                        "issue": "Pod has no security context defined",
                        "recommendation": "Define a security context for the pod"
                    })
                
                if pod.spec.volumes:
                    for volume in pod.spec.volumes:
                        if hasattr(volume, "host_path") and volume.host_path:
                            pod_data["issues"].append({
                                "severity": "high",
                                "issue": f"Pod uses host path volume: {volume.host_path.path}",
                                "recommendation": "Avoid using host path volumes as they can lead to container escapes"
                            })
                
                for container in pod.spec.containers:
                    if container.security_context and container.security_context.privileged:
                        pod_data["issues"].append({
                            "severity": "high",
                            "issue": f"Container {container.name} runs in privileged mode",
                            "recommendation": "Avoid running containers in privileged mode"
                        })
                    
                    if container.image.endswith(":latest") or ":" not in container.image:
                        pod_data["issues"].append({
                            "severity": "medium",
                            "issue": f"Container {container.name} uses 'latest' tag or no tag",
                            "recommendation": "Use specific version tags for container images"
                        })
                    
                    if not container.resources or not container.resources.limits:
                        pod_data["issues"].append({
                            "severity": "medium",
                            "issue": f"Container {container.name} has no resource limits",
                            "recommendation": "Set resource limits for all containers"
                        })
                
                if pod.spec.host_network:
                    pod_data["issues"].append({
                        "severity": "high",
                        "issue": "Pod uses host network",
                        "recommendation": "Avoid using host network as it can lead to container escapes"
                    })
                
                if pod.spec.host_pid:
                    pod_data["issues"].append({
                        "severity": "high",
                        "issue": "Pod uses host PID namespace",
                        "recommendation": "Avoid using host PID namespace as it can lead to container escapes"
                    })
                
                if pod.spec.host_ipc:
                    pod_data["issues"].append({
                        "severity": "high",
                        "issue": "Pod uses host IPC namespace",
                        "recommendation": "Avoid using host IPC namespace as it can lead to container escapes"
                    })
                
                results.append(pod_data)
            
            all_issues = []
            for pod_data in results:
                for issue in pod_data["issues"]:
                    all_issues.append({
                        "pod": pod_data["name"],
                        "namespace": pod_data["namespace"],
                        "severity": issue["severity"],
                        "issue": issue["issue"],
                        "recommendation": issue["recommendation"]
                    })
            
            return {
                "status": "success",
                "pod_count": len(results),
                "pods_with_issues": sum(1 for pod in results if pod["issues"]),
                "total_issues": len(all_issues),
                "high_severity_issues": sum(1 for issue in all_issues if issue["severity"] == "high"),
                "medium_severity_issues": sum(1 for issue in all_issues if issue["severity"] == "medium"),
                "low_severity_issues": sum(1 for issue in all_issues if issue["severity"] == "low"),
                "detailed_results": results,
                "issues_summary": all_issues
            }
        except ApiException as e:
            return {
                "status": "error",
                "error": f"Failed to enforce security best practices: {e.reason}",
                "details": e.body
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to enforce security best practices: {str(e)}"
            }
    
    def secure_kubernetes_api(self) -> Dict[str, Any]:
        """Check the security of the Kubernetes API server configuration."""
        try:
            api_server_pods = self.core_v1.list_namespaced_pod(
                namespace="kube-system",
                label_selector="component=kube-apiserver"
            )
            
            if not api_server_pods.items:
                return {
                    "status": "warning",
                    "message": "Could not find kube-apiserver pod in kube-system namespace. This may be expected in managed Kubernetes services."
                }
            
            results = {
                "api_server_pods": [],
                "security_issues": []
            }
            
            for pod in api_server_pods.items:
                pod_data = {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "api_server_args": {}
                }
                
                for container in pod.spec.containers:
                    if container.name == "kube-apiserver":
                        if container.command:
                            for cmd in container.command:
                                if cmd.startswith("--"):
                                    parts = cmd.split("=", 1)
                                    if len(parts) == 2:
                                        key = parts[0].lstrip("-")
                                        value = parts[1]
                                        pod_data["api_server_args"][key] = value
                        
                        if container.args:
                            for arg in container.args:
                                if arg.startswith("--"):
                                    parts = arg.split("=", 1)
                                    if len(parts) == 2:
                                        key = parts[0].lstrip("-")
                                        value = parts[1]
                                        pod_data["api_server_args"][key] = value
                
                results["api_server_pods"].append(pod_data)
                
                args = pod_data["api_server_args"]
                
                if args.get("anonymous-auth") == "true":
                    results["security_issues"].append({
                        "severity": "high",
                        "issue": "Anonymous authentication is enabled",
                        "recommendation": "Disable anonymous authentication by setting --anonymous-auth=false"
                    })
                
                if "basic-auth-file" in args:
                    results["security_issues"].append({
                        "severity": "high",
                        "issue": "Basic authentication is enabled",
                        "recommendation": "Disable basic authentication by removing --basic-auth-file"
                    })
                
                if "token-auth-file" in args:
                    results["security_issues"].append({
                        "severity": "high",
                        "issue": "Token authentication is enabled",
                        "recommendation": "Disable token authentication by removing --token-auth-file"
                    })
                
                if "insecure-port" in args and args["insecure-port"] != "0":
                    results["security_issues"].append({
                        "severity": "high",
                        "issue": "Insecure port is enabled",
                        "recommendation": "Disable insecure port by setting --insecure-port=0"
                    })
                
                if "secure-port" not in args:
                    results["security_issues"].append({
                        "severity": "high",
                        "issue": "Secure port is not explicitly set",
                        "recommendation": "Set secure port explicitly with --secure-port=6443"
                    })
                
                if "audit-log-path" not in args:
                    results["security_issues"].append({
                        "severity": "medium",
                        "issue": "Audit logging is not enabled",
                        "recommendation": "Enable audit logging by setting --audit-log-path"
                    })
                
                if "authorization-mode" not in args:
                    results["security_issues"].append({
                        "severity": "high",
                        "issue": "Authorization mode is not explicitly set",
                        "recommendation": "Set authorization mode explicitly with --authorization-mode=Node,RBAC"
                    })
                elif "RBAC" not in args["authorization-mode"]:
                    results["security_issues"].append({
                        "severity": "high",
                        "issue": "RBAC authorization is not enabled",
                        "recommendation": "Enable RBAC authorization by including RBAC in --authorization-mode"
                    })
                
                if "enable-admission-plugins" not in args:
                    results["security_issues"].append({
                        "severity": "medium",
                        "issue": "Admission plugins are not explicitly enabled",
                        "recommendation": "Enable recommended admission plugins"
                    })
                else:
                    recommended_plugins = [
                        "NodeRestriction",
                        "PodSecurityPolicy",
                        "AlwaysPullImages",
                        "ServiceAccount"
                    ]
                    enabled_plugins = args["enable-admission-plugins"].split(",")
                    missing_plugins = [plugin for plugin in recommended_plugins if plugin not in enabled_plugins]
                    if missing_plugins:
                        results["security_issues"].append({
                            "severity": "medium",
                            "issue": f"Some recommended admission plugins are not enabled: {', '.join(missing_plugins)}",
                            "recommendation": f"Enable these admission plugins: {', '.join(missing_plugins)}"
                        })
            
            return {
                "status": "success",
                "api_server_count": len(results["api_server_pods"]),
                "security_issues_count": len(results["security_issues"]),
                "high_severity_issues": sum(1 for issue in results["security_issues"] if issue["severity"] == "high"),
                "medium_severity_issues": sum(1 for issue in results["security_issues"] if issue["severity"] == "medium"),
                "low_severity_issues": sum(1 for issue in results["security_issues"] if issue["severity"] == "low"),
                "detailed_results": results
            }
        except ApiException as e:
            return {
                "status": "error",
                "error": f"Failed to check API server security: {e.reason}",
                "details": e.body
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to check API server security: {str(e)}"
            }
