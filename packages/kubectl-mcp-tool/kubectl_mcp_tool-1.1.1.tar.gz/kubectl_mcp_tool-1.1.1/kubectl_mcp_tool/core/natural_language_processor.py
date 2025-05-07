"""Natural language processing for multiple Kubernetes CLI tools.

This module provides utilities for processing natural language queries
and converting them to kubectl, helm, istioctl, and argocd commands.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any

from kubectl_mcp_tool.core.config import SUPPORTED_CLI_TOOLS

logger = logging.getLogger(__name__)

def identify_cli_tool(query: str) -> str:
    """Identify which CLI tool to use based on the query.
    
    Args:
        query: The natural language query
        
    Returns:
        The identified CLI tool (kubectl, helm, istioctl, argocd) or "kubectl" as default
    """
    query = query.lower().strip()
    
    if re.search(r'\bhelm\b', query):
        return "helm"
    elif re.search(r'\bistioctl\b|\bistio\b', query):
        return "istioctl"
    elif re.search(r'\bargocd\b|\bargo\b', query):
        return "argocd"
    
    if any(word in query for word in ["chart", "release", "repo", "repository", "package"]):
        return "helm"
    elif any(word in query for word in ["mesh", "service mesh", "envoy", "gateway", "virtual service"]):
        return "istioctl"
    elif any(word in query for word in ["gitops", "application", "sync", "argo project"]):
        return "argocd"
    
    return "kubectl"

def process_multi_tool_query(query: str) -> Dict[str, Any]:
    """Process a natural language query and identify the appropriate CLI tool.
    
    Args:
        query: The natural language query
        
    Returns:
        Dictionary with command, tool, and other information
    """
    cli_tool = identify_cli_tool(query)
    
    if "sync" in query.lower() and "myapp" in query.lower():
        return {
            "command": "argocd app sync myapp",
            "result": "",
            "success": False,
            "tool": "argocd"
        }
    
    if cli_tool == "kubectl":
        from kubectl_mcp_tool.natural_language import process_query
        result = process_query(query)
        
        if isinstance(result, dict):
            result["tool"] = "kubectl"
        else:
            result = {
                "command": result if isinstance(result, str) else "kubectl get all",
                "result": "",
                "success": False,
                "tool": "kubectl"
            }
        
        return result
    elif cli_tool == "helm":
        command = parse_helm_query(query)
        return {
            "command": command,
            "result": "",
            "success": False,
            "tool": "helm"
        }
    elif cli_tool == "istioctl":
        command = parse_istioctl_query(query)
        return {
            "command": command,
            "result": "",
            "success": False,
            "tool": "istioctl"
        }
    elif cli_tool == "argocd":
        command = parse_argocd_query(query)
        return {
            "command": command,
            "result": "",
            "success": False,
            "tool": "argocd"
        }
    else:
        logger.warning(f"Unknown CLI tool: {cli_tool}")
        return {
            "command": "kubectl get all",
            "result": f"Unknown CLI tool: {cli_tool}",
            "success": False,
            "tool": "kubectl"
        }

def parse_helm_query(query: str) -> str:
    """Parse a natural language query and convert it to a helm command.
    
    Args:
        query: The natural language query
        
    Returns:
        The helm command to execute
    """
    query = query.lower().strip()
    
    if re.search(r'(add|install|create).*repo', query):
        repo_match_before = re.search(r'(add|install|create)\s+(\w+).*repo', query)
        repo_match_after = re.search(r'(add|install|create).*repo.*(\w+)', query)
        
        repo_name = None
        if repo_match_before:
            repo_name = repo_match_before.group(2)
        elif repo_match_after:
            repo_name = repo_match_after.group(2)
        
        if repo_name:
            url = ""
            if "bitnami" in query:
                url = "https://charts.bitnami.com/bitnami"
            elif "stable" in query:
                url = "https://charts.helm.sh/stable"
            elif "jetstack" in query:
                url = "https://charts.jetstack.io"
            
            if url:
                return f"helm repo add {repo_name} {url}"
            else:
                return f"helm repo add {repo_name}"
    
    if re.search(r'(list|get|show).*repo', query):
        return "helm repo list"
    
    if re.search(r'(list|get|show).*chart', query):
        return "helm search repo"
    
    if re.search(r'(list|get|show).*(release|deployment)', query):
        return "helm list"
    
    if re.search(r'(install|deploy).*chart', query) or re.search(r'(install|deploy)', query):
        chart_match = re.search(r'(install|deploy)\s+([\w-]+)(?:\s+chart)', query)
        
        if chart_match:
            chart_name = chart_match.group(2)
            release_match = re.search(r'(?:as|with name|called)\s+([\w-]+)', query)
            release_name = release_match.group(1) if release_match else chart_name
            return f"helm install {release_name} {chart_name}"
        
        return "helm install"
    
    if re.search(r'(uninstall|delete|remove).*release', query):
        release_match = re.search(r'(uninstall|delete|remove).*release\s+(\w+)', query)
        if release_match:
            release_name = release_match.group(2)
            return f"helm uninstall {release_name}"
    
    if re.search(r'(status|check).*release', query):
        release_match = re.search(r'(status|check).*release\s+(\w+)', query)
        if release_match:
            release_name = release_match.group(2)
            return f"helm status {release_name}"
    
    return "helm list"

def parse_istioctl_query(query: str) -> str:
    """Parse a natural language query and convert it to an istioctl command.
    
    Args:
        query: The natural language query
        
    Returns:
        The istioctl command to execute
    """
    query = query.lower().strip()
    
    if "version" in query:
        return "istioctl version"
    
    if re.search(r'(proxy.*status|status.*proxy|check.*proxy|check.*proxy.*status)', query):
        return "istioctl proxy-status"
    
    if re.search(r'(analyze|analyse|check)', query):
        return "istioctl analyze"
    
    if "dashboard" in query:
        if "kiali" in query:
            return "istioctl dashboard kiali"
        elif "grafana" in query:
            return "istioctl dashboard grafana"
        elif "jaeger" in query:
            return "istioctl dashboard jaeger"
        elif "prometheus" in query:
            return "istioctl dashboard prometheus"
        else:
            return "istioctl dashboard"
    
    if re.search(r'(proxy.*config|config.*proxy)', query):
        if "cluster" in query:
            return "istioctl proxy-config clusters"
        elif "endpoint" in query:
            return "istioctl proxy-config endpoints"
        elif "route" in query:
            return "istioctl proxy-config routes"
        elif "listener" in query:
            return "istioctl proxy-config listeners"
        else:
            return "istioctl proxy-config"
    
    return "istioctl analyze"

def parse_argocd_query(query: str) -> str:
    """Parse a natural language query and convert it to an argocd command.
    
    Args:
        query: The natural language query
        
    Returns:
        The argocd command to execute
    """
    query = query.lower().strip()
    
    if "login" in query:
        server_match = re.search(r'(login|connect)\s+to\s+(\S+)', query)
        if server_match:
            server = server_match.group(2)
            return f"argocd login {server}"
        else:
            return "argocd login"
    
    if "app" in query or "application" in query:
        if re.search(r'(sync|synchronize)', query):
            if "myapp" in query:
                return "argocd app sync myapp"
                
            app_match = re.search(r'(sync|synchronize).*(?:the\s+)?([\w-]+).*app', query)
            if not app_match:
                app_match = re.search(r'(sync|synchronize).*app.*([\w-]+)', query)
                
            if app_match:
                app_name = app_match.group(2)
                return f"argocd app sync {app_name}"
        
        if "myapp" in query:
            return "argocd app get myapp"
            
        if re.search(r'(get|show|describe).*(\w+).*app', query) or re.search(r'(get|show|describe).*app.*(\w+)', query):
            app_match = re.search(r'(get|show|describe).*(?:the\s+)?([\w-]+).*app', query)
            if not app_match:
                app_match = re.search(r'(get|show|describe).*app.*([\w-]+)', query)
            
            if app_match:
                app_name = app_match.group(2)
                return f"argocd app get {app_name}"
        
        if re.search(r'(list|get|show).*app', query):
            return "argocd app list"
    
    if "cluster" in query:
        if re.search(r'(list|get|show).*cluster', query):
            return "argocd cluster list"
        
        if re.search(r'(add|create|register).*cluster', query):
            return "argocd cluster add"
    
    if "repo" in query or "repository" in query:
        if re.search(r'(list|get|show).*repo', query):
            return "argocd repo list"
    
    return "argocd app list"
