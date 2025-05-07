"""
Advanced features module for kubectl-mcp-tool.

This module provides advanced functionality for Kubernetes operations,
including custom resource definitions, cross-namespace operations,
batch operations, resource relationship mapping, and volume management.
"""

import os
import json
import logging
import re
import yaml
from typing import Dict, Any, List, Optional, Tuple, Set
import subprocess
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class KubernetesAdvancedFeatures:
    """Advanced Kubernetes operations."""
    
    def __init__(self):
        """Initialize Kubernetes client."""
        try:
            config.load_kube_config()
            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.custom_objects_api = client.CustomObjectsApi()
            self.storage_v1 = client.StorageV1Api()
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

    def get_custom_resources(self, group: str, version: str, plural: str, 
                           namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get custom resources of a specific type."""
        try:
            if namespace:
                resources = self.custom_objects_api.list_namespaced_custom_object(
                    group=group,
                    version=version,
                    namespace=namespace,
                    plural=plural
                )
            else:
                resources = self.custom_objects_api.list_cluster_custom_object(
                    group=group,
                    version=version,
                    plural=plural
                )
            
            return {
                "status": "success",
                "resources": resources.get("items", []),
                "count": len(resources.get("items", []))
            }
        except ApiException as e:
            logger.error(f"Failed to get custom resources: {e}")
            return {
                "status": "error",
                "error": f"API error: {e.reason}",
                "details": e.body
            }
        except Exception as e:
            logger.error(f"Failed to get custom resources: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def get_custom_resource_definitions(self) -> Dict[str, Any]:
        """Get all custom resource definitions in the cluster."""
        try:
            cmd = ["kubectl", "get", "crd", "-o", "json"]
            result = self.run_command(cmd)
            
            if result.startswith("Error"):
                return {
                    "status": "error",
                    "error": result
                }
            
            try:
                data = json.loads(result)
                crds = []
                
                for item in data.get("items", []):
                    crd_info = {
                        "name": item.get("metadata", {}).get("name"),
                        "group": item.get("spec", {}).get("group"),
                        "version": item.get("spec", {}).get("version") or 
                                  item.get("spec", {}).get("versions", [{}])[0].get("name"),
                        "plural": item.get("spec", {}).get("names", {}).get("plural"),
                        "singular": item.get("spec", {}).get("names", {}).get("singular"),
                        "kind": item.get("spec", {}).get("names", {}).get("kind"),
                        "scope": item.get("spec", {}).get("scope")
                    }
                    crds.append(crd_info)
                
                return {
                    "status": "success",
                    "crds": crds,
                    "count": len(crds)
                }
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "error": "Failed to parse CRD data"
                }
        except Exception as e:
            logger.error(f"Failed to get CRDs: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def create_custom_resource(self, group: str, version: str, plural: str, 
                             namespace: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom resource."""
        try:
            result = self.custom_objects_api.create_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                body=body
            )
            
            return {
                "status": "success",
                "message": f"Custom resource {body.get('metadata', {}).get('name')} created",
                "resource": result
            }
        except ApiException as e:
            logger.error(f"Failed to create custom resource: {e}")
            return {
                "status": "error",
                "error": f"API error: {e.reason}",
                "details": e.body
            }
        except Exception as e:
            logger.error(f"Failed to create custom resource: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def cross_namespace_operation(self, operation: str, resource_type: str, 
                                namespaces: List[str], selector: Optional[str] = None) -> Dict[str, Any]:
        """Perform operations across multiple namespaces."""
        try:
            results = {}
            
            for namespace in namespaces:
                cmd = ["kubectl", operation, resource_type]
                
                if selector:
                    cmd.extend(["-l", selector])
                
                cmd.extend(["-n", namespace])
                
                result = self.run_command(cmd)
                results[namespace] = result
            
            success_count = sum(1 for r in results.values() if not r.startswith("Error"))
            error_count = len(results) - success_count
            
            return {
                "status": "success" if error_count == 0 else "partial_success" if success_count > 0 else "error",
                "operation": operation,
                "resource_type": resource_type,
                "results": results,
                "namespaces": namespaces,
                "success_count": success_count,
                "error_count": error_count
            }
        except Exception as e:
            logger.error(f"Failed to perform cross-namespace operation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def batch_operation(self, operation: str, resources: List[Dict[str, str]]) -> Dict[str, Any]:
        """Perform batch operations on multiple resources."""
        try:
            results = []
            
            for resource in resources:
                resource_type = resource.get("type")
                resource_name = resource.get("name")
                namespace = resource.get("namespace")
                
                cmd = ["kubectl", operation, f"{resource_type}/{resource_name}"]
                
                if namespace:
                    cmd.extend(["-n", namespace])
                
                result = self.run_command(cmd)
                
                results.append({
                    "resource_type": resource_type,
                    "resource_name": resource_name,
                    "namespace": namespace,
                    "result": result,
                    "success": not result.startswith("Error")
                })
            
            success_count = sum(1 for r in results if r["success"])
            error_count = len(results) - success_count
            
            return {
                "status": "success" if error_count == 0 else "partial_success" if success_count > 0 else "error",
                "operation": operation,
                "results": results,
                "success_count": success_count,
                "error_count": error_count
            }
        except Exception as e:
            logger.error(f"Failed to perform batch operation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def map_resource_relationships(self, resource_type: str, resource_name: str, 
                                 namespace: Optional[str] = None) -> Dict[str, Any]:
        """Map relationships between Kubernetes resources."""
        try:
            relationships = {
                "depends_on": [],
                "dependents": []
            }
            
            cmd = ["kubectl", "get", f"{resource_type}/{resource_name}", "-o", "json"]
            if namespace:
                cmd.extend(["-n", namespace])
            
            result = self.run_command(cmd)
            
            if result.startswith("Error"):
                return {
                    "status": "error",
                    "error": result
                }
            
            try:
                resource = json.loads(result)
                
                if resource_type == "pod":
                    for volume in resource.get("spec", {}).get("volumes", []):
                        if volume.get("persistentVolumeClaim"):
                            relationships["depends_on"].append({
                                "type": "persistentvolumeclaim",
                                "name": volume["persistentVolumeClaim"]["claimName"],
                                "namespace": namespace
                            })
                        if volume.get("configMap"):
                            relationships["depends_on"].append({
                                "type": "configmap",
                                "name": volume["configMap"]["name"],
                                "namespace": namespace
                            })
                        if volume.get("secret"):
                            relationships["depends_on"].append({
                                "type": "secret",
                                "name": volume["secret"]["secretName"],
                                "namespace": namespace
                            })
                    
                    for owner_ref in resource.get("metadata", {}).get("ownerReferences", []):
                        relationships["depends_on"].append({
                            "type": owner_ref["kind"].lower(),
                            "name": owner_ref["name"],
                            "namespace": namespace
                        })
                
                elif resource_type == "deployment" or resource_type == "statefulset":
                    selector = self._get_selector_from_resource(resource)
                    if selector:
                        cmd = ["kubectl", "get", "pods", "-l", selector, "-o", "json"]
                        if namespace:
                            cmd.extend(["-n", namespace])
                        
                        pods_result = self.run_command(cmd)
                        if not pods_result.startswith("Error"):
                            try:
                                pods_data = json.loads(pods_result)
                                for pod in pods_data.get("items", []):
                                    relationships["dependents"].append({
                                        "type": "pod",
                                        "name": pod["metadata"]["name"],
                                        "namespace": pod["metadata"]["namespace"]
                                    })
                            except json.JSONDecodeError:
                                pass
                
                elif resource_type == "service":
                    selector = self._get_selector_from_resource(resource)
                    if selector:
                        cmd = ["kubectl", "get", "pods", "-l", selector, "-o", "json"]
                        if namespace:
                            cmd.extend(["-n", namespace])
                        
                        pods_result = self.run_command(cmd)
                        if not pods_result.startswith("Error"):
                            try:
                                pods_data = json.loads(pods_result)
                                for pod in pods_data.get("items", []):
                                    relationships["dependents"].append({
                                        "type": "pod",
                                        "name": pod["metadata"]["name"],
                                        "namespace": pod["metadata"]["namespace"]
                                    })
                            except json.JSONDecodeError:
                                pass
                
                elif resource_type == "persistentvolumeclaim":
                    pv_name = resource.get("spec", {}).get("volumeName")
                    if pv_name:
                        relationships["depends_on"].append({
                            "type": "persistentvolume",
                            "name": pv_name
                        })
                    
                    cmd = ["kubectl", "get", "pods", "-o", "json"]
                    if namespace:
                        cmd.extend(["-n", namespace])
                    
                    pods_result = self.run_command(cmd)
                    if not pods_result.startswith("Error"):
                        try:
                            pods_data = json.loads(pods_result)
                            for pod in pods_data.get("items", []):
                                for volume in pod.get("spec", {}).get("volumes", []):
                                    if volume.get("persistentVolumeClaim", {}).get("claimName") == resource_name:
                                        relationships["dependents"].append({
                                            "type": "pod",
                                            "name": pod["metadata"]["name"],
                                            "namespace": pod["metadata"]["namespace"]
                                        })
                        except json.JSONDecodeError:
                            pass
                
                return {
                    "status": "success",
                    "resource_type": resource_type,
                    "resource_name": resource_name,
                    "namespace": namespace,
                    "relationships": relationships
                }
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "error": "Failed to parse resource data"
                }
        except Exception as e:
            logger.error(f"Failed to map resource relationships: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _get_selector_from_resource(self, resource: Dict[str, Any]) -> Optional[str]:
        """Extract selector from a resource."""
        selector = resource.get("spec", {}).get("selector", {})
        if not selector:
            return None
        
        match_labels = selector.get("matchLabels")
        if match_labels:
            return ",".join([f"{k}={v}" for k, v in match_labels.items()])
        
        if isinstance(selector, dict) and not any(k in ["matchLabels", "matchExpressions"] for k in selector.keys()):
            return ",".join([f"{k}={v}" for k, v in selector.items()])
        
        return None

    def explain_error(self, error_message: str) -> Dict[str, Any]:
        """Explain Kubernetes errors and suggest recovery actions."""
        common_errors = {
            "ImagePullBackOff": {
                "explanation": "Kubernetes cannot pull the container image from the registry.",
                "suggestions": [
                    "Verify the image name and tag are correct",
                    "Check if the image exists in the registry",
                    "Ensure the cluster has access to the image registry",
                    "Check if authentication is required for the registry"
                ]
            },
            "CrashLoopBackOff": {
                "explanation": "The container is crashing repeatedly, causing Kubernetes to back off from restarting it.",
                "suggestions": [
                    "Check container logs for error messages",
                    "Verify the container command and arguments",
                    "Ensure the container has sufficient resources",
                    "Check if the application inside the container is configured correctly"
                ]
            },
            "OOMKilled": {
                "explanation": "The container was terminated because it exceeded its memory limit.",
                "suggestions": [
                    "Increase the memory limit for the container",
                    "Optimize the application to use less memory",
                    "Check for memory leaks in the application"
                ]
            },
            "ContainerCreating": {
                "explanation": "The container is still being created.",
                "suggestions": [
                    "Wait for the container to finish creating",
                    "Check if there are issues with the node",
                    "Verify that volumes can be mounted correctly",
                    "Check if the container image is large and still downloading"
                ]
            },
            "ErrImagePull": {
                "explanation": "There was an error pulling the container image.",
                "suggestions": [
                    "Verify the image name and tag are correct",
                    "Check if the image exists in the registry",
                    "Ensure the cluster has access to the image registry",
                    "Check if authentication is required for the registry"
                ]
            },
            "CreateContainerConfigError": {
                "explanation": "There was an error creating the container due to configuration issues.",
                "suggestions": [
                    "Check if referenced ConfigMaps or Secrets exist",
                    "Verify volume mounts are correctly specified",
                    "Ensure environment variables are properly defined"
                ]
            },
            "InvalidImageName": {
                "explanation": "The specified image name is invalid.",
                "suggestions": [
                    "Verify the image name follows the correct format",
                    "Check for typos in the image name",
                    "Ensure the image registry is correctly specified"
                ]
            },
            "forbidden": {
                "explanation": "The operation was forbidden due to RBAC restrictions.",
                "suggestions": [
                    "Check if the service account has the necessary permissions",
                    "Verify RBAC roles and role bindings",
                    "Ensure the user or service account has access to the resource"
                ]
            },
            "not found": {
                "explanation": "The requested resource was not found.",
                "suggestions": [
                    "Verify the resource name is correct",
                    "Check if the resource exists in the specified namespace",
                    "Ensure you're using the correct API version"
                ]
            },
            "timed out": {
                "explanation": "The operation timed out.",
                "suggestions": [
                    "Check network connectivity",
                    "Verify the Kubernetes API server is responsive",
                    "Increase the timeout value if possible",
                    "Check if the cluster is under heavy load"
                ]
            }
        }
        
        matches = []
        for error_key, error_info in common_errors.items():
            if error_key.lower() in error_message.lower():
                matches.append({
                    "error_type": error_key,
                    "explanation": error_info["explanation"],
                    "suggestions": error_info["suggestions"]
                })
        
        if not matches:
            if "permission" in error_message.lower() or "authorize" in error_message.lower():
                matches.append({
                    "error_type": "Permission Error",
                    "explanation": "You don't have sufficient permissions to perform this operation.",
                    "suggestions": [
                        "Check your RBAC permissions",
                        "Verify your service account has the necessary roles",
                        "Ask a cluster administrator for the required permissions"
                    ]
                })
            elif "connect" in error_message.lower() or "connection" in error_message.lower():
                matches.append({
                    "error_type": "Connection Error",
                    "explanation": "There was an issue connecting to the Kubernetes API server or another service.",
                    "suggestions": [
                        "Check network connectivity",
                        "Verify the Kubernetes API server is running",
                        "Ensure your kubeconfig is correctly configured",
                        "Check if there are firewall rules blocking the connection"
                    ]
                })
        
        return {
            "status": "success",
            "error_message": error_message,
            "matches": matches,
            "match_count": len(matches)
        }

    def manage_volumes(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Manage and identify volumes in the cluster."""
        try:
            pvs = self.core_v1.list_persistent_volume()
            
            if namespace:
                pvcs = self.core_v1.list_namespaced_persistent_volume_claim(namespace=namespace)
            else:
                pvcs = self.core_v1.list_persistent_volume_claim_for_all_namespaces()
            
            storage_classes = self.storage_v1.list_storage_class()
            
            pv_list = []
            for pv in pvs.items:
                pv_info = {
                    "name": pv.metadata.name,
                    "capacity": pv.spec.capacity.get("storage"),
                    "access_modes": pv.spec.access_modes,
                    "reclaim_policy": pv.spec.persistent_volume_reclaim_policy,
                    "status": pv.status.phase,
                    "storage_class": pv.spec.storage_class_name,
                    "claim": f"{pv.spec.claim_ref.namespace}/{pv.spec.claim_ref.name}" if pv.spec.claim_ref else None
                }
                pv_list.append(pv_info)
            
            pvc_list = []
            for pvc in pvcs.items:
                pvc_info = {
                    "name": pvc.metadata.name,
                    "namespace": pvc.metadata.namespace,
                    "status": pvc.status.phase,
                    "volume": pvc.spec.volume_name,
                    "storage_class": pvc.spec.storage_class_name,
                    "access_modes": pvc.spec.access_modes,
                    "capacity": pvc.status.capacity.get("storage") if pvc.status.capacity else None
                }
                pvc_list.append(pvc_info)
            
            sc_list = []
            for sc in storage_classes.items:
                sc_info = {
                    "name": sc.metadata.name,
                    "provisioner": sc.provisioner,
                    "reclaim_policy": sc.reclaim_policy,
                    "volume_binding_mode": sc.volume_binding_mode,
                    "is_default": sc.metadata.annotations.get("storageclass.kubernetes.io/is-default-class") == "true" if sc.metadata.annotations else False
                }
                sc_list.append(sc_info)
            
            pod_volumes = []
            if namespace:
                pods = self.core_v1.list_namespaced_pod(namespace=namespace)
            else:
                pods = self.core_v1.list_pod_for_all_namespaces()
            
            for pod in pods.items:
                for volume in pod.spec.volumes or []:
                    if volume.persistent_volume_claim:
                        pod_volumes.append({
                            "pod": pod.metadata.name,
                            "namespace": pod.metadata.namespace,
                            "volume_name": volume.name,
                            "pvc_name": volume.persistent_volume_claim.claim_name
                        })
            
            return {
                "status": "success",
                "persistent_volumes": pv_list,
                "persistent_volume_claims": pvc_list,
                "storage_classes": sc_list,
                "pod_volumes": pod_volumes,
                "counts": {
                    "persistent_volumes": len(pv_list),
                    "persistent_volume_claims": len(pvc_list),
                    "storage_classes": len(sc_list),
                    "pod_volumes": len(pod_volumes)
                }
            }
        except Exception as e:
            logger.error(f"Failed to manage volumes: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
