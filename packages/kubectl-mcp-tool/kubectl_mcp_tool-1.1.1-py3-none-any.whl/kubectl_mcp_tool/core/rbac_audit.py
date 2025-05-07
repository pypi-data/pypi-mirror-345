import logging
from typing import Dict, List, Optional, Any, Tuple
from kubernetes import client
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class KubernetesRBACAudit:
    """Class for auditing RBAC permissions in Kubernetes clusters."""
    
    def __init__(self, api_client=None):
        """Initialize the KubernetesRBACAudit class."""
        self.api_client = api_client or client.ApiClient()
        self.core_v1 = client.CoreV1Api(self.api_client)
        self.rbac_v1 = client.RbacAuthorizationV1Api(self.api_client)
    
    def audit_rbac_permissions(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Audit RBAC permissions in the cluster or namespace."""
        try:
            results = {
                "service_accounts": [],
                "roles": [],
                "role_bindings": [],
                "cluster_roles": [],
                "cluster_role_bindings": []
            }
            
            if namespace:
                service_accounts = self.core_v1.list_namespaced_service_account(namespace=namespace)
            else:
                service_accounts = self.core_v1.list_service_account_for_all_namespaces()
            
            for sa in service_accounts.items:
                results["service_accounts"].append({
                    "name": sa.metadata.name,
                    "namespace": sa.metadata.namespace,
                    "secrets": [secret.name for secret in sa.secrets] if sa.secrets else []
                })
            
            if namespace:
                roles = self.rbac_v1.list_namespaced_role(namespace=namespace)
            else:
                roles = self.rbac_v1.list_role_for_all_namespaces()
            
            for role in roles.items:
                role_data = {
                    "name": role.metadata.name,
                    "namespace": role.metadata.namespace,
                    "rules": []
                }
                
                for rule in role.rules:
                    rule_data = {
                        "api_groups": rule.api_groups,
                        "resources": rule.resources,
                        "verbs": rule.verbs
                    }
                    if rule.resource_names:
                        rule_data["resource_names"] = rule.resource_names
                    
                    role_data["rules"].append(rule_data)
                
                results["roles"].append(role_data)
            
            if namespace:
                role_bindings = self.rbac_v1.list_namespaced_role_binding(namespace=namespace)
            else:
                role_bindings = self.rbac_v1.list_role_binding_for_all_namespaces()
            
            for rb in role_bindings.items:
                rb_data = {
                    "name": rb.metadata.name,
                    "namespace": rb.metadata.namespace,
                    "role_ref": {
                        "kind": rb.role_ref.kind,
                        "name": rb.role_ref.name,
                        "api_group": rb.role_ref.api_group
                    },
                    "subjects": []
                }
                
                for subject in rb.subjects:
                    subject_data = {
                        "kind": subject.kind,
                        "name": subject.name
                    }
                    if subject.namespace:
                        subject_data["namespace"] = subject.namespace
                    
                    rb_data["subjects"].append(subject_data)
                
                results["role_bindings"].append(rb_data)
            
            cluster_roles = self.rbac_v1.list_cluster_role()
            
            for cr in cluster_roles.items:
                if cr.metadata.name.startswith("system:"):
                    continue
                
                cr_data = {
                    "name": cr.metadata.name,
                    "rules": []
                }
                
                for rule in cr.rules:
                    rule_data = {
                        "api_groups": rule.api_groups,
                        "resources": rule.resources,
                        "verbs": rule.verbs
                    }
                    if rule.resource_names:
                        rule_data["resource_names"] = rule.resource_names
                    
                    cr_data["rules"].append(rule_data)
                
                results["cluster_roles"].append(cr_data)
            
            cluster_role_bindings = self.rbac_v1.list_cluster_role_binding()
            
            for crb in cluster_role_bindings.items:
                if crb.metadata.name.startswith("system:"):
                    continue
                
                crb_data = {
                    "name": crb.metadata.name,
                    "role_ref": {
                        "kind": crb.role_ref.kind,
                        "name": crb.role_ref.name,
                        "api_group": crb.role_ref.api_group
                    },
                    "subjects": []
                }
                
                for subject in crb.subjects:
                    subject_data = {
                        "kind": subject.kind,
                        "name": subject.name
                    }
                    if subject.namespace:
                        subject_data["namespace"] = subject.namespace
                    
                    crb_data["subjects"].append(subject_data)
                
                results["cluster_role_bindings"].append(crb_data)
            
            security_issues = []
            
            for crb in results["cluster_role_bindings"]:
                if crb["role_ref"]["name"] == "cluster-admin":
                    for subject in crb["subjects"]:
                        if subject["kind"] == "ServiceAccount":
                            security_issues.append({
                                "severity": "high",
                                "issue": f"ServiceAccount {subject.get('name')} in namespace {subject.get('namespace', 'unknown')} has cluster-admin privileges",
                                "recommendation": "Review if this service account really needs cluster-admin privileges. Consider using more restrictive roles."
                            })
            
            for role in results["roles"]:
                for rule in role["rules"]:
                    if "*" in rule["resources"] and "*" in rule["verbs"]:
                        security_issues.append({
                            "severity": "medium",
                            "issue": f"Role {role['name']} in namespace {role['namespace']} has wildcard resources and verbs",
                            "recommendation": "Specify only the resources and verbs that are actually needed."
                        })
            
            for cr in results["cluster_roles"]:
                for rule in cr["rules"]:
                    if "*" in rule["resources"] and "*" in rule["verbs"]:
                        security_issues.append({
                            "severity": "high",
                            "issue": f"ClusterRole {cr['name']} has wildcard resources and verbs",
                            "recommendation": "Specify only the resources and verbs that are actually needed."
                        })
            
            return {
                "status": "success",
                "audit_results": results,
                "security_issues": security_issues,
                "counts": {
                    "service_accounts": len(results["service_accounts"]),
                    "roles": len(results["roles"]),
                    "role_bindings": len(results["role_bindings"]),
                    "cluster_roles": len(results["cluster_roles"]),
                    "cluster_role_bindings": len(results["cluster_role_bindings"]),
                    "security_issues": len(security_issues)
                }
            }
        except ApiException as e:
            return {
                "status": "error",
                "error": f"Failed to audit RBAC permissions: {e.reason}",
                "details": e.body
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to audit RBAC permissions: {str(e)}"
            }
