"""Security validation for Kubernetes MCP Tool.

This module provides security validation for Kubernetes CLI commands,
including command validation, security checks, and safety measures.
"""

import logging
import re
import shlex
from typing import Dict, List, Optional, Set, Tuple

from kubectl_mcp_tool.core.config import ALLOWED_UNIX_COMMANDS, SECURITY_MODE

logger = logging.getLogger(__name__)

DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"dd\s+if=/dev/zero\s+of=/dev/sd[a-z]",
    r"mkfs\s+/dev/sd[a-z]",
    r"dd\s+if=/dev/urandom\s+of=/dev/sd[a-z]",
    r":\(\)\{\s+:\|:\s+&\s+\};\s+:",  # Fork bomb
    r"sudo\s+rm\s+-rf\s+/",
    r">\s+/dev/sd[a-z]",
    r">\s+/dev/null\s+2>&1\s+&",
    r">\s+/dev/zero",
    r">\s+/dev/random",
    r">\s+/dev/urandom",
]

STRICT_ALLOWED_KUBECTL = [
    "get", "describe", "explain", "version", "config", "api-resources",
    "api-versions", "cluster-info", "top", "auth", "logs"
]

STANDARD_DISALLOWED_KUBECTL = [
    "delete", "exec", "cp", "attach", "debug", "port-forward", "proxy",
    "run", "scale", "cordon", "drain", "taint", "uncordon", "replace",
    "patch", "edit", "apply", "create", "rollout", "expose", "autoscale",
    "label", "annotate", "completion", "alpha", "auth", "certificate",
    "set", "wait", "kustomize"
]

STRICT_ALLOWED_ISTIOCTL = [
    "analyze", "proxy-status", "proxy-config", "version", "dashboard",
    "profile", "manifest", "verify-install", "ps", "x", "authz"
]

STRICT_ALLOWED_HELM = [
    "list", "status", "get", "history", "show", "inspect", "verify",
    "version", "env", "plugin", "search", "repo", "completion"
]

STRICT_ALLOWED_ARGOCD = [
    "app", "cluster", "context", "login", "logout", "proj", "repo",
    "version", "account", "cert", "gpg"
]


async def validate_command(command: str) -> None:
    """Validate a command against security rules.
    
    Args:
        command: The command to validate
        
    Raises:
        CommandValidationError: If the command fails validation
    """
    from kubectl_mcp_tool.core.errors import CommandValidationError
    from kubectl_mcp_tool.core.tools import is_pipe_command, split_pipe_command
    
    if SECURITY_MODE == "permissive":
        logger.debug(f"Permissive mode: skipping validation for command: {command}")
        return
    
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command):
            message = f"Command contains dangerous pattern: {pattern}"
            logger.warning(message)
            raise CommandValidationError(message, {"command": command, "pattern": pattern})
    
    if is_pipe_command(command):
        commands = split_pipe_command(command)
        
        for cmd in commands:
            await validate_single_command(cmd)
    else:
        await validate_single_command(command)


async def validate_single_command(command: str) -> None:
    """Validate a single command against security rules.
    
    Args:
        command: The command to validate
        
    Raises:
        CommandValidationError: If the command fails validation
    """
    from kubectl_mcp_tool.core.errors import CommandValidationError
    
    try:
        parts = shlex.split(command)
        if not parts:
            return
        
        cmd = parts[0]
        
        if cmd == "kubectl" and len(parts) > 1:
            subcmd = parts[1]
            
            if SECURITY_MODE == "strict" and subcmd not in STRICT_ALLOWED_KUBECTL:
                message = f"kubectl command not allowed in strict mode: {subcmd}"
                logger.warning(message)
                raise CommandValidationError(message, {"command": command, "subcmd": subcmd})
            
            if SECURITY_MODE == "standard" and subcmd in STANDARD_DISALLOWED_KUBECTL:
                message = f"kubectl command not allowed in standard mode: {subcmd}"
                logger.warning(message)
                raise CommandValidationError(message, {"command": command, "subcmd": subcmd})
        
        elif cmd == "istioctl" and len(parts) > 1:
            subcmd = parts[1]
            
            if SECURITY_MODE == "strict" and subcmd not in STRICT_ALLOWED_ISTIOCTL:
                message = f"istioctl command not allowed in strict mode: {subcmd}"
                logger.warning(message)
                raise CommandValidationError(message, {"command": command, "subcmd": subcmd})
        
        elif cmd == "helm" and len(parts) > 1:
            subcmd = parts[1]
            
            if SECURITY_MODE == "strict" and subcmd not in STRICT_ALLOWED_HELM:
                message = f"helm command not allowed in strict mode: {subcmd}"
                logger.warning(message)
                raise CommandValidationError(message, {"command": command, "subcmd": subcmd})
        
        elif cmd == "argocd" and len(parts) > 1:
            subcmd = parts[1]
            
            if SECURITY_MODE == "strict" and subcmd not in STRICT_ALLOWED_ARGOCD:
                message = f"argocd command not allowed in strict mode: {subcmd}"
                logger.warning(message)
                raise CommandValidationError(message, {"command": command, "subcmd": subcmd})
        
        elif cmd in ALLOWED_UNIX_COMMANDS:
            pass
        
        elif cmd not in ["kubectl", "istioctl", "helm", "argocd"]:
            message = f"Command not allowed: {cmd}"
            logger.warning(message)
            raise CommandValidationError(message, {"command": command, "cmd": cmd})
    
    except Exception as e:
        if isinstance(e, CommandValidationError):
            raise
        
        message = f"Error validating command: {e}"
        logger.error(message)
        raise CommandValidationError(message, {"command": command})
