"""Prompt templates for common Kubernetes operations.

This module defines a collection of prompt templates for common Kubernetes operations,
providing structured prompts to ensure best practices and efficient resource management.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def register_prompt_templates() -> None:
    """Register prompt templates with the MCP server.
    
    This function is called by the MCP server to register all prompt templates.
    """
    logger.info("Registering prompt templates")
    return

def register_prompts(server) -> None:
    """Register prompt templates with the MCP server.
    
    Args:
        server: The MCP server instance
    """
    logger.info("Registering prompt templates")
    
    for prompt_func in [
        status_check_prompts,
        deployment_prompts,
        troubleshooting_prompts,
        inventory_prompts,
        security_prompts,
        scaling_prompts,
        logs_prompts,
        istio_prompts,
        helm_prompts,
        argocd_prompts,
    ]:
        try:
            prompts = prompt_func()
            for prompt in prompts:
                server.register_prompt_template(
                    prompt["name"],
                    prompt["description"],
                    prompt["template"]
                )
            logger.info(f"Registered {len(prompts)} prompts from {prompt_func.__name__}")
        except Exception as e:
            logger.error(f"Error registering prompts from {prompt_func.__name__}: {e}")


def status_check_prompts() -> List[Dict[str, str]]:
    """Generate prompts for checking resource status.
    
    Returns:
        List of prompt templates
    """
    return [
        {
            "name": "check_pod_status",
            "description": "Check the status of pods in a namespace",
            "template": "kubectl get pods -n {{namespace}} {{selector}}",
        },
        {
            "name": "check_deployment_status",
            "description": "Check the status of deployments in a namespace",
            "template": "kubectl get deployments -n {{namespace}} {{selector}}",
        },
        {
            "name": "check_service_status",
            "description": "Check the status of services in a namespace",
            "template": "kubectl get services -n {{namespace}} {{selector}}",
        },
        {
            "name": "check_node_status",
            "description": "Check the status of nodes in the cluster",
            "template": "kubectl get nodes {{selector}}",
        },
        {
            "name": "check_cluster_health",
            "description": "Check the overall health of the cluster",
            "template": "kubectl get componentstatuses",
        },
    ]


def deployment_prompts() -> List[Dict[str, str]]:
    """Generate prompts for deploying applications.
    
    Returns:
        List of prompt templates
    """
    return [
        {
            "name": "deploy_from_yaml",
            "description": "Deploy resources from a YAML file",
            "template": "kubectl apply -f {{filename}} -n {{namespace}}",
        },
        {
            "name": "deploy_simple_pod",
            "description": "Deploy a simple pod with a single container",
            "template": "kubectl run {{name}} --image={{image}} -n {{namespace}} {{args}}",
        },
        {
            "name": "create_deployment",
            "description": "Create a deployment with multiple replicas",
            "template": "kubectl create deployment {{name}} --image={{image}} --replicas={{replicas}} -n {{namespace}}",
        },
        {
            "name": "expose_deployment",
            "description": "Expose a deployment as a service",
            "template": "kubectl expose deployment {{name}} --port={{port}} --target-port={{target_port}} --type={{type}} -n {{namespace}}",
        },
    ]


def troubleshooting_prompts() -> List[Dict[str, str]]:
    """Generate prompts for troubleshooting issues.
    
    Returns:
        List of prompt templates
    """
    return [
        {
            "name": "describe_pod",
            "description": "Get detailed information about a pod",
            "template": "kubectl describe pod {{name}} -n {{namespace}}",
        },
        {
            "name": "get_pod_logs",
            "description": "Get logs from a pod",
            "template": "kubectl logs {{name}} -n {{namespace}} {{container}} {{tail}}",
        },
        {
            "name": "get_events",
            "description": "Get events in a namespace",
            "template": "kubectl get events -n {{namespace}} {{selector}}",
        },
        {
            "name": "check_pod_resources",
            "description": "Check resource usage of pods",
            "template": "kubectl top pod -n {{namespace}} {{selector}}",
        },
        {
            "name": "check_node_resources",
            "description": "Check resource usage of nodes",
            "template": "kubectl top node {{selector}}",
        },
    ]


def inventory_prompts() -> List[Dict[str, str]]:
    """Generate prompts for inventorying resources.
    
    Returns:
        List of prompt templates
    """
    return [
        {
            "name": "list_all_resources",
            "description": "List all resources in a namespace",
            "template": "kubectl get all -n {{namespace}}",
        },
        {
            "name": "list_api_resources",
            "description": "List all available API resources",
            "template": "kubectl api-resources",
        },
        {
            "name": "list_namespaces",
            "description": "List all namespaces in the cluster",
            "template": "kubectl get namespaces",
        },
        {
            "name": "list_custom_resources",
            "description": "List custom resources of a specific type",
            "template": "kubectl get {{resource_type}} -n {{namespace}}",
        },
    ]


def security_prompts() -> List[Dict[str, str]]:
    """Generate prompts for security checks.
    
    Returns:
        List of prompt templates
    """
    return [
        {
            "name": "check_rbac",
            "description": "Check RBAC permissions",
            "template": "kubectl auth can-i {{verb}} {{resource}} -n {{namespace}}",
        },
        {
            "name": "list_service_accounts",
            "description": "List service accounts in a namespace",
            "template": "kubectl get serviceaccounts -n {{namespace}}",
        },
        {
            "name": "list_roles",
            "description": "List roles in a namespace",
            "template": "kubectl get roles -n {{namespace}}",
        },
        {
            "name": "list_role_bindings",
            "description": "List role bindings in a namespace",
            "template": "kubectl get rolebindings -n {{namespace}}",
        },
        {
            "name": "list_cluster_roles",
            "description": "List cluster roles",
            "template": "kubectl get clusterroles",
        },
        {
            "name": "list_cluster_role_bindings",
            "description": "List cluster role bindings",
            "template": "kubectl get clusterrolebindings",
        },
    ]


def scaling_prompts() -> List[Dict[str, str]]:
    """Generate prompts for scaling resources.
    
    Returns:
        List of prompt templates
    """
    return [
        {
            "name": "scale_deployment",
            "description": "Scale a deployment to a specific number of replicas",
            "template": "kubectl scale deployment {{name}} --replicas={{replicas}} -n {{namespace}}",
        },
        {
            "name": "scale_statefulset",
            "description": "Scale a statefulset to a specific number of replicas",
            "template": "kubectl scale statefulset {{name}} --replicas={{replicas}} -n {{namespace}}",
        },
        {
            "name": "autoscale_deployment",
            "description": "Configure horizontal pod autoscaling for a deployment",
            "template": "kubectl autoscale deployment {{name}} --min={{min}} --max={{max}} --cpu-percent={{cpu_percent}} -n {{namespace}}",
        },
    ]


def logs_prompts() -> List[Dict[str, str]]:
    """Generate prompts for analyzing logs.
    
    Returns:
        List of prompt templates
    """
    return [
        {
            "name": "get_recent_logs",
            "description": "Get recent logs from a pod",
            "template": "kubectl logs {{name}} -n {{namespace}} --tail={{tail}}",
        },
        {
            "name": "follow_logs",
            "description": "Follow logs from a pod",
            "template": "kubectl logs {{name}} -n {{namespace}} -f",
        },
        {
            "name": "get_previous_logs",
            "description": "Get logs from a previous container instance",
            "template": "kubectl logs {{name}} -n {{namespace}} -p",
        },
        {
            "name": "get_logs_since",
            "description": "Get logs since a specific time",
            "template": "kubectl logs {{name}} -n {{namespace}} --since={{since}}",
        },
    ]


def istio_prompts() -> List[Dict[str, str]]:
    """Generate prompts for Istio service mesh operations.
    
    Returns:
        List of prompt templates
    """
    return [
        {
            "name": "check_istio_status",
            "description": "Check the status of Istio components",
            "template": "istioctl proxy-status",
        },
        {
            "name": "analyze_mesh",
            "description": "Analyze the service mesh for potential issues",
            "template": "istioctl analyze -n {{namespace}}",
        },
        {
            "name": "get_virtual_services",
            "description": "Get virtual services in a namespace",
            "template": "kubectl get virtualservices -n {{namespace}}",
        },
        {
            "name": "get_gateways",
            "description": "Get gateways in a namespace",
            "template": "kubectl get gateways -n {{namespace}}",
        },
        {
            "name": "get_service_entries",
            "description": "Get service entries in a namespace",
            "template": "kubectl get serviceentries -n {{namespace}}",
        },
    ]


def helm_prompts() -> List[Dict[str, str]]:
    """Generate prompts for Helm chart management.
    
    Returns:
        List of prompt templates
    """
    return [
        {
            "name": "list_helm_releases",
            "description": "List all Helm releases",
            "template": "helm list -A",
        },
        {
            "name": "install_helm_chart",
            "description": "Install a Helm chart",
            "template": "helm install {{name}} {{chart}} -n {{namespace}} {{values}}",
        },
        {
            "name": "upgrade_helm_chart",
            "description": "Upgrade a Helm chart",
            "template": "helm upgrade {{name}} {{chart}} -n {{namespace}} {{values}}",
        },
        {
            "name": "uninstall_helm_chart",
            "description": "Uninstall a Helm chart",
            "template": "helm uninstall {{name}} -n {{namespace}}",
        },
        {
            "name": "get_helm_release_status",
            "description": "Get the status of a Helm release",
            "template": "helm status {{name}} -n {{namespace}}",
        },
    ]


def argocd_prompts() -> List[Dict[str, str]]:
    """Generate prompts for ArgoCD application management.
    
    Returns:
        List of prompt templates
    """
    return [
        {
            "name": "list_argocd_apps",
            "description": "List all ArgoCD applications",
            "template": "argocd app list",
        },
        {
            "name": "get_argocd_app",
            "description": "Get details of an ArgoCD application",
            "template": "argocd app get {{name}}",
        },
        {
            "name": "sync_argocd_app",
            "description": "Sync an ArgoCD application",
            "template": "argocd app sync {{name}}",
        },
        {
            "name": "list_argocd_projects",
            "description": "List all ArgoCD projects",
            "template": "argocd proj list",
        },
        {
            "name": "list_argocd_repos",
            "description": "List all ArgoCD repositories",
            "template": "argocd repo list",
        },
    ]
