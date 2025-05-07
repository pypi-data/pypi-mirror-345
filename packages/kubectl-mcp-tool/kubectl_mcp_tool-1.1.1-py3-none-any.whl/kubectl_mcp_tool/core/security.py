"""
Kubernetes security module.

This module provides functionality for security operations in Kubernetes clusters,
including RBAC validation, security context auditing, and security best practices.
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

class KubernetesSecurity:
    """Kubernetes security operations."""
    
    def __init__(self):
        """Initialize Kubernetes client."""
        try:
            config.load_kube_config()
            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.rbac_v1 = client.RbacAuthorizationV1Api()
            self.networking_v1 = client.NetworkingV1Api()
            self.policy_v1beta1 = None
            
            try:
                self.policy_v1beta1 = client.PolicyV1beta1Api()
            except Exception as e:
                logger.warning(f"PolicyV1beta1 API not available: {e}")
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
            
    def validate_rbac(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Validate RBAC configuration in the cluster or namespace."""
        try:
            if namespace:
                roles = self.rbac_v1.list_namespaced_role(namespace=namespace)
                role_bindings = self.rbac_v1.list_namespaced_role_binding(namespace=namespace)
            else:
                roles = self.rbac_v1.list_role_for_all_namespaces()
                role_bindings = self.rbac_v1.list_role_binding_for_all_namespaces()
            
            cluster_roles = self.rbac_v1.list_cluster_role()
            cluster_role_bindings = self.rbac_v1.list_cluster_role_binding()
            
            role_analysis = []
            for role in roles.items:
                role_info = {
                    "name": role.metadata.name,
                    "namespace": role.metadata.namespace,
                    "rules": [
                        {
                            "api_groups": rule.api_groups,
                            "resources": rule.resources,
                            "verbs": rule.verbs,
                            "resource_names": rule.resource_names
                        } for rule in role.rules
                    ],
                    "bindings": []
                }
                
                for binding in role_bindings.items:
                    if binding.role_ref.kind == "Role" and binding.role_ref.name == role.metadata.name:
                        role_info["bindings"].append({
                            "name": binding.metadata.name,
                            "namespace": binding.metadata.namespace,
                            "subjects": [
                                {
                                    "kind": subject.kind,
                                    "name": subject.name,
                                    "namespace": subject.namespace
                                } for subject in binding.subjects
                            ]
                        })
                
                sensitive_permissions = self._check_sensitive_permissions(role.rules)
                if sensitive_permissions:
                    role_info["sensitive_permissions"] = sensitive_permissions
                
                role_analysis.append(role_info)
            
            cluster_role_analysis = []
            for role in cluster_roles.items:
                role_info = {
                    "name": role.metadata.name,
                    "rules": [
                        {
                            "api_groups": rule.api_groups,
                            "resources": rule.resources,
                            "verbs": rule.verbs,
                            "resource_names": rule.resource_names
                        } for rule in role.rules
                    ],
                    "bindings": []
                }
                
                for binding in cluster_role_bindings.items:
                    if binding.role_ref.kind == "ClusterRole" and binding.role_ref.name == role.metadata.name:
                        role_info["bindings"].append({
                            "name": binding.metadata.name,
                            "subjects": [
                                {
                                    "kind": subject.kind,
                                    "name": subject.name,
                                    "namespace": subject.namespace
                                } for subject in binding.subjects
                            ]
                        })
                
                sensitive_permissions = self._check_sensitive_permissions(role.rules)
                if sensitive_permissions:
                    role_info["sensitive_permissions"] = sensitive_permissions
                
                cluster_role_analysis.append(role_info)
            
            issues = []
            
            for role in role_analysis:
                for rule in role["rules"]:
                    if "*" in rule["resources"] and "*" in rule["verbs"]:
                        issues.append({
                            "severity": "high",
                            "type": "wildcard_permissions",
                            "message": f"Role {role['name']} in namespace {role['namespace']} has wildcard permissions",
                            "details": rule
                        })
            
            for role in cluster_role_analysis:
                for rule in role["rules"]:
                    if "*" in rule["resources"] and "*" in rule["verbs"]:
                        issues.append({
                            "severity": "high",
                            "type": "wildcard_permissions",
                            "message": f"ClusterRole {role['name']} has wildcard permissions",
                            "details": rule
                        })
            
            service_accounts_with_admin = []
            for role in cluster_role_analysis:
                if role["name"] == "cluster-admin":
                    for binding in role["bindings"]:
                        for subject in binding["subjects"]:
                            if subject["kind"] == "ServiceAccount":
                                service_accounts_with_admin.append({
                                    "name": subject["name"],
                                    "namespace": subject["namespace"],
                                    "binding": binding["name"]
                                })
                                
                                issues.append({
                                    "severity": "high",
                                    "type": "service_account_admin",
                                    "message": f"ServiceAccount {subject['name']} in namespace {subject['namespace']} has cluster-admin permissions",
                                    "details": {
                                        "binding": binding["name"]
                                    }
                                })
            
            return {
                "roles": role_analysis,
                "cluster_roles": cluster_role_analysis,
                "issues": issues,
                "service_accounts_with_admin": service_accounts_with_admin,
                "total_roles": len(role_analysis),
                "total_cluster_roles": len(cluster_role_analysis),
                "total_issues": len(issues)
            }
        except Exception as e:
            logger.error(f"Failed to validate RBAC: {e}")
            return {
                "error": str(e)
            }

    def _check_sensitive_permissions(self, rules: List[Any]) -> List[Dict[str, Any]]:
        """Check for sensitive permissions in RBAC rules."""
        sensitive_permissions = []
        
        sensitive_resources = [
            "secrets", "configmaps", "pods/exec", "pods/attach", "pods/proxy",
            "services/proxy", "nodes/proxy", "certificatesigningrequests"
        ]
        
        sensitive_verbs = ["create", "update", "patch", "delete", "deletecollection"]
        
        for rule in rules:
            resources = rule.resources or []
            verbs = rule.verbs or []
            
            for resource in resources:
                if resource in sensitive_resources or resource == "*":
                    for verb in verbs:
                        if verb in sensitive_verbs or verb == "*":
                            sensitive_permissions.append({
                                "resource": resource,
                                "verb": verb,
                                "api_groups": rule.api_groups
                            })
        
        return sensitive_permissions
        
    def audit_security_contexts(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Audit security contexts of pods and containers."""
        try:
            if namespace:
                pods = self.core_v1.list_namespaced_pod(namespace=namespace)
            else:
                pods = self.core_v1.list_pod_for_all_namespaces()
            
            results = []
            issues = []
            
            for pod in pods.items:
                pod_security = {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "pod_security_context": None,
                    "containers": []
                }
                
                if pod.spec.security_context:
                    pod_security["pod_security_context"] = {
                        "run_as_user": pod.spec.security_context.run_as_user,
                        "run_as_group": pod.spec.security_context.run_as_group,
                        "fs_group": pod.spec.security_context.fs_group,
                        "run_as_non_root": pod.spec.security_context.run_as_non_root,
                        "privileged": False,  # Pod-level doesn't have privileged
                        "allow_privilege_escalation": False  # Pod-level doesn't have this
                    }
                
                for container in pod.spec.containers:
                    container_security = {
                        "name": container.name,
                        "security_context": None
                    }
                    
                    if container.security_context:
                        container_security["security_context"] = {
                            "run_as_user": container.security_context.run_as_user,
                            "run_as_group": container.security_context.run_as_group,
                            "run_as_non_root": container.security_context.run_as_non_root,
                            "privileged": container.security_context.privileged,
                            "allow_privilege_escalation": container.security_context.allow_privilege_escalation,
                            "read_only_root_filesystem": container.security_context.read_only_root_filesystem,
                            "capabilities": {
                                "add": container.security_context.capabilities.add if container.security_context.capabilities else None,
                                "drop": container.security_context.capabilities.drop if container.security_context.capabilities else None
                            } if container.security_context.capabilities else None
                        }
                        
                        if container.security_context.privileged:
                            issues.append({
                                "severity": "high",
                                "type": "privileged_container",
                                "message": f"Container {container.name} in pod {pod.metadata.name} (namespace {pod.metadata.namespace}) is running as privileged",
                                "pod": pod.metadata.name,
                                "container": container.name,
                                "namespace": pod.metadata.namespace
                            })
                        
                        if container.security_context.allow_privilege_escalation:
                            issues.append({
                                "severity": "medium",
                                "type": "privilege_escalation",
                                "message": f"Container {container.name} in pod {pod.metadata.name} (namespace {pod.metadata.namespace}) allows privilege escalation",
                                "pod": pod.metadata.name,
                                "container": container.name,
                                "namespace": pod.metadata.namespace
                            })
                        
                        if container.security_context.capabilities and container.security_context.capabilities.add:
                            for cap in container.security_context.capabilities.add:
                                if cap in ["ALL", "SYS_ADMIN", "NET_ADMIN"]:
                                    issues.append({
                                        "severity": "high",
                                        "type": "dangerous_capability",
                                        "message": f"Container {container.name} in pod {pod.metadata.name} (namespace {pod.metadata.namespace}) has dangerous capability: {cap}",
                                        "pod": pod.metadata.name,
                                        "container": container.name,
                                        "namespace": pod.metadata.namespace,
                                        "capability": cap
                                    })
                    else:
                        issues.append({
                            "severity": "low",
                            "type": "missing_security_context",
                            "message": f"Container {container.name} in pod {pod.metadata.name} (namespace {pod.metadata.namespace}) has no security context defined",
                            "pod": pod.metadata.name,
                            "container": container.name,
                            "namespace": pod.metadata.namespace
                        })
                    
                    pod_security["containers"].append(container_security)
                
                for volume in pod.spec.volumes or []:
                    if volume.host_path:
                        issues.append({
                            "severity": "high",
                            "type": "host_path_volume",
                            "message": f"Pod {pod.metadata.name} (namespace {pod.metadata.namespace}) uses host path volume: {volume.host_path.path}",
                            "pod": pod.metadata.name,
                            "namespace": pod.metadata.namespace,
                            "volume": volume.name,
                            "path": volume.host_path.path
                        })
                
                if pod.spec.host_network:
                    issues.append({
                        "severity": "high",
                        "type": "host_network",
                        "message": f"Pod {pod.metadata.name} (namespace {pod.metadata.namespace}) uses host network",
                        "pod": pod.metadata.name,
                        "namespace": pod.metadata.namespace
                    })
                
                if pod.spec.host_pid:
                    issues.append({
                        "severity": "high",
                        "type": "host_pid",
                        "message": f"Pod {pod.metadata.name} (namespace {pod.metadata.namespace}) uses host PID namespace",
                        "pod": pod.metadata.name,
                        "namespace": pod.metadata.namespace
                    })
                
                if pod.spec.host_ipc:
                    issues.append({
                        "severity": "high",
                        "type": "host_ipc",
                        "message": f"Pod {pod.metadata.name} (namespace {pod.metadata.namespace}) uses host IPC namespace",
                        "pod": pod.metadata.name,
                        "namespace": pod.metadata.namespace
                    })
                
                results.append(pod_security)
            
            issue_summary = {}
            for issue in issues:
                issue_type = issue["type"]
                if issue_type not in issue_summary:
                    issue_summary[issue_type] = {
                        "count": 0,
                        "severity": issue["severity"]
                    }
                issue_summary[issue_type]["count"] += 1
            
            return {
                "pods": results,
                "issues": issues,
                "issue_summary": issue_summary,
                "total_pods": len(results),
                "total_issues": len(issues)
            }
        except Exception as e:
            logger.error(f"Failed to audit security contexts: {e}")
            return {
                "error": str(e)
            }
            
    def assess_network_policies(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Assess network policies in the cluster or namespace."""
        try:
            if namespace:
                network_policies = self.networking_v1.list_namespaced_network_policy(namespace=namespace)
            else:
                network_policies = self.networking_v1.list_network_policy_for_all_namespaces()
            
            namespaces = self.core_v1.list_namespace()
            namespace_list = [ns.metadata.name for ns in namespaces.items]
            
            if namespace:
                pods = self.core_v1.list_namespaced_pod(namespace=namespace)
                pod_namespaces = [namespace]
            else:
                pods = self.core_v1.list_pod_for_all_namespaces()
                pod_namespaces = list(set(pod.metadata.namespace for pod in pods.items))
            
            policy_analysis = []
            for policy in network_policies.items:
                policy_info = {
                    "name": policy.metadata.name,
                    "namespace": policy.metadata.namespace,
                    "pod_selector": policy.spec.pod_selector.match_labels if policy.spec.pod_selector else {},
                    "ingress_rules": [],
                    "egress_rules": []
                }
                
                if policy.spec.ingress:
                    for rule in policy.spec.ingress:
                        ingress_rule = {
                            "from_sources": [],
                            "ports": []
                        }
                        
                        if hasattr(rule, 'from_') and rule.from_:
                            for from_item in rule.from_:
                                if from_item.ip_block:
                                    ingress_rule["from_sources"].append({
                                        "type": "ip_block",
                                        "cidr": from_item.ip_block.cidr,
                                        "except": from_item.ip_block.except_ if hasattr(from_item.ip_block, "except_") else None
                                    })
                                elif from_item.namespace_selector:
                                    ingress_rule["from_sources"].append({
                                        "type": "namespace_selector",
                                        "match_labels": from_item.namespace_selector.match_labels if from_item.namespace_selector.match_labels else {}
                                    })
                                elif from_item.pod_selector:
                                    ingress_rule["from_sources"].append({
                                        "type": "pod_selector",
                                        "match_labels": from_item.pod_selector.match_labels if from_item.pod_selector.match_labels else {}
                                    })
                        
                        if rule.ports:
                            for port in rule.ports:
                                ingress_rule["ports"].append({
                                    "port": port.port,
                                    "protocol": port.protocol
                                })
                        
                        policy_info["ingress_rules"].append(ingress_rule)
                
                if policy.spec.egress:
                    for rule in policy.spec.egress:
                        egress_rule = {
                            "to": [],
                            "ports": []
                        }
                        
                        if hasattr(rule, 'to') and rule.to:
                            for to_item in rule.to:
                                if to_item.ip_block:
                                    egress_rule["to"].append({
                                        "type": "ip_block",
                                        "cidr": to_item.ip_block.cidr,
                                        "except": to_item.ip_block.except_ if hasattr(to_item.ip_block, "except_") else None
                                    })
                                elif to_item.namespace_selector:
                                    egress_rule["to"].append({
                                        "type": "namespace_selector",
                                        "match_labels": to_item.namespace_selector.match_labels if to_item.namespace_selector.match_labels else {}
                                    })
                                elif to_item.pod_selector:
                                    egress_rule["to"].append({
                                        "type": "pod_selector",
                                        "match_labels": to_item.pod_selector.match_labels if to_item.pod_selector.match_labels else {}
                                    })
                        
                        if rule.ports:
                            for port in rule.ports:
                                egress_rule["ports"].append({
                                    "port": port.port,
                                    "protocol": port.protocol
                                })
                        
                        policy_info["egress_rules"].append(egress_rule)
                
                if policy.spec.policy_types:
                    policy_info["policy_types"] = policy.spec.policy_types
                else:
                    policy_types = ["Ingress"]
                    if policy.spec.egress:
                        policy_types.append("Egress")
                    policy_info["policy_types"] = policy_types
                
                policy_analysis.append(policy_info)
            
            namespaces_without_policies = []
            for ns in namespace_list:
                if ns in pod_namespaces:  # Only check namespaces with pods
                    has_policy = False
                    for policy in network_policies.items:
                        if policy.metadata.namespace == ns:
                            has_policy = True
                            break
                    
                    if not has_policy:
                        namespaces_without_policies.append(ns)
            
            issues = []
            
            for ns in namespaces_without_policies:
                issues.append({
                    "severity": "medium",
                    "type": "namespace_without_network_policy",
                    "message": f"Namespace {ns} has pods but no network policies",
                    "namespace": ns
                })
            
            for policy in policy_analysis:
                for rule in policy["ingress_rules"]:
                    if not rule["from"]:
                        issues.append({
                            "severity": "medium",
                            "type": "permissive_ingress",
                            "message": f"Network policy {policy['name']} in namespace {policy['namespace']} allows ingress from any source",
                            "policy": policy["name"],
                            "namespace": policy["namespace"]
                        })
                
                for rule in policy["egress_rules"]:
                    if not rule["to"]:
                        issues.append({
                            "severity": "medium",
                            "type": "permissive_egress",
                            "message": f"Network policy {policy['name']} in namespace {policy['namespace']} allows egress to any destination",
                            "policy": policy["name"],
                            "namespace": policy["namespace"]
                        })
            
            return {
                "network_policies": policy_analysis,
                "namespaces_without_policies": namespaces_without_policies,
                "issues": issues,
                "total_policies": len(policy_analysis),
                "total_issues": len(issues)
            }
        except Exception as e:
            logger.error(f"Failed to assess network policies: {e}")
            return {
                "error": str(e)
            }
            
    def create_role(self, name: str, rules: List[Dict[str, Any]], namespace: str) -> Dict[str, Any]:
        """Create a Role in the specified namespace."""
        try:
            k8s_rules = []
            for rule in rules:
                k8s_rule = client.V1PolicyRule(
                    api_groups=rule.get("api_groups", [""]),
                    resources=rule.get("resources", []),
                    verbs=rule.get("verbs", []),
                    resource_names=rule.get("resource_names")
                )
                k8s_rules.append(k8s_rule)
            
            role = client.V1Role(
                metadata=client.V1ObjectMeta(name=name),
                rules=k8s_rules
            )
            
            result = self.rbac_v1.create_namespaced_role(
                namespace=namespace,
                body=role
            )
            
            return {
                "status": "success",
                "message": f"Role {name} created in namespace {namespace}",
                "name": result.metadata.name,
                "namespace": result.metadata.namespace
            }
        except ApiException as e:
            return {
                "status": "error",
                "error": f"Failed to create role: {e.reason}",
                "details": e.body
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to create role: {str(e)}"
            }
            
    def create_cluster_role(self, name: str, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a ClusterRole."""
        try:
            k8s_rules = []
            for rule in rules:
                k8s_rule = client.V1PolicyRule(
                    api_groups=rule.get("api_groups", [""]),
                    resources=rule.get("resources", []),
                    verbs=rule.get("verbs", []),
                    resource_names=rule.get("resource_names")
                )
                k8s_rules.append(k8s_rule)
            
            cluster_role = client.V1ClusterRole(
                metadata=client.V1ObjectMeta(name=name),
                rules=k8s_rules
            )
            
            result = self.rbac_v1.create_cluster_role(
                body=cluster_role
            )
            
            return {
                "status": "success",
                "message": f"ClusterRole {name} created",
                "name": result.metadata.name
            }
        except ApiException as e:
            return {
                "status": "error",
                "error": f"Failed to create cluster role: {e.reason}",
                "details": e.body
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to create cluster role: {str(e)}"
            }
            
    def create_role_binding(self, name: str, role_name: str, subjects: List[Dict[str, Any]], 
                           namespace: str, role_kind: str = "Role") -> Dict[str, Any]:
        """Create a RoleBinding in the specified namespace."""
        try:
            k8s_subjects = []
            for subject in subjects:
                k8s_subject = client.V1Subject(
                    kind=subject.get("kind"),
                    name=subject.get("name"),
                    namespace=subject.get("namespace")
                )
                k8s_subjects.append(k8s_subject)
            
            role_binding = client.V1RoleBinding(
                metadata=client.V1ObjectMeta(name=name),
                role_ref=client.V1RoleRef(
                    api_group="rbac.authorization.k8s.io",
                    kind=role_kind,
                    name=role_name
                ),
                subjects=k8s_subjects
            )
            
            result = self.rbac_v1.create_namespaced_role_binding(
                namespace=namespace,
                body=role_binding
            )
            
            return {
                "status": "success",
                "message": f"RoleBinding {name} created in namespace {namespace}",
                "name": result.metadata.name,
                "namespace": result.metadata.namespace
            }
        except ApiException as e:
            return {
                "status": "error",
                "error": f"Failed to create role binding: {e.reason}",
                "details": e.body
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to create role binding: {str(e)}"
            }
            
    def create_service_account(self, name: str, namespace: str, 
                              annotations: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a ServiceAccount in the specified namespace."""
        try:
            service_account = client.V1ServiceAccount(
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace,
                    annotations=annotations
                )
            )
            
            result = self.core_v1.create_namespaced_service_account(
                namespace=namespace,
                body=service_account
            )
            
            return {
                "status": "success",
                "message": f"ServiceAccount {name} created in namespace {namespace}",
                "name": result.metadata.name,
                "namespace": result.metadata.namespace
            }
        except ApiException as e:
            return {
                "status": "error",
                "error": f"Failed to create service account: {e.reason}",
                "details": e.body
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to create service account: {str(e)}"
            }
