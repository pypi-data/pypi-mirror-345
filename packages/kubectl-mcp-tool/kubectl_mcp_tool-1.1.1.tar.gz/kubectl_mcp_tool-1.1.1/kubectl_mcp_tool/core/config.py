"""Configuration settings for Kubernetes MCP Tool.

This module contains configuration settings for the Kubernetes MCP Tool,
including environment variables, constants, and default values.
"""

import os
from typing import Dict, Any

ENV_TIMEOUT = "KUBECTL_MCP_TIMEOUT"
ENV_MAX_OUTPUT = "KUBECTL_MCP_MAX_OUTPUT"
ENV_TRANSPORT = "KUBECTL_MCP_TRANSPORT"
ENV_K8S_CONTEXT = "KUBECTL_MCP_K8S_CONTEXT"
ENV_K8S_NAMESPACE = "KUBECTL_MCP_K8S_NAMESPACE"
ENV_SECURITY_MODE = "KUBECTL_MCP_SECURITY_MODE"

DEFAULT_TIMEOUT = int(os.environ.get(ENV_TIMEOUT, "300"))  # 5 minutes
MAX_OUTPUT_SIZE = int(os.environ.get(ENV_MAX_OUTPUT, "102400"))  # 100KB
DEFAULT_TRANSPORT = os.environ.get(ENV_TRANSPORT, "stdio")  # stdio, sse, http
DEFAULT_K8S_CONTEXT = os.environ.get(ENV_K8S_CONTEXT, "")
DEFAULT_K8S_NAMESPACE = os.environ.get(ENV_K8S_NAMESPACE, "default")
SECURITY_MODE = os.environ.get(ENV_SECURITY_MODE, "standard")  # strict, standard, permissive

SECURITY_CONFIG_PATH = os.environ.get(
    "KUBECTL_MCP_SECURITY_CONFIG",
    os.path.join(os.path.expanduser("~"), ".kube", "mcp-security.yaml")
)

LOG_DIR = os.path.join(os.path.expanduser("~"), ".kube", "mcp-logs")
os.makedirs(LOG_DIR, exist_ok=True)

SUPPORTED_CLI_TOOLS: Dict[str, Dict[str, str]] = {
    "kubectl": {
        "check_command": "kubectl version --client",
        "help_command": "kubectl --help",
        "description": "Kubernetes command-line tool"
    },
    "istioctl": {
        "check_command": "istioctl version --remote=false",
        "help_command": "istioctl --help",
        "description": "Command-line tool for Istio service mesh"
    },
    "helm": {
        "check_command": "helm version",
        "help_command": "helm --help",
        "description": "Kubernetes package manager"
    },
    "argocd": {
        "check_command": "argocd version --client",
        "help_command": "argocd --help",
        "description": "GitOps continuous delivery tool for Kubernetes"
    }
}

ALLOWED_UNIX_COMMANDS = [
    "grep", "awk", "sed", "sort", "uniq", "head", "tail", "wc",
    "cut", "tr", "column", "jq", "yq", "cat", "less", "more",
    "tee", "xargs", "find", "ls", "ps", "top", "watch"
]

SERVER_INSTRUCTIONS = """

This server provides a standardized interface for executing commands from various Kubernetes CLI tools:

- kubectl: Kubernetes command-line tool
- istioctl: Command-line tool for Istio service mesh
- helm: Kubernetes package manager
- argocd: GitOps continuous delivery tool for Kubernetes


You can execute commands using the following format:

```
<cli_tool> <command> [args...]
```

For example:
```
kubectl get pods -n default
istioctl analyze
helm list
argocd app list
```

You can also use Unix pipes to filter and transform the output:
```
kubectl get pods -n default | grep Running
kubectl get pods -A | grep -v Running | wc -l
```


The server includes built-in prompt templates for common Kubernetes operations:

- Status checking
- Deployment
- Troubleshooting
- Resource inventory
- Security checks
- Scaling
- Logs analysis
- Service mesh operations
- Helm chart management
- ArgoCD application management


Commands are validated against security rules to prevent dangerous operations.
The security mode can be set to:

- strict: Rejects all potentially dangerous commands
- standard: Allows some potentially dangerous commands with warnings
- permissive: Allows all commands without validation


Commands have a default timeout of 5 minutes and a maximum output size of 100KB.
These limits can be configured using environment variables.
"""
