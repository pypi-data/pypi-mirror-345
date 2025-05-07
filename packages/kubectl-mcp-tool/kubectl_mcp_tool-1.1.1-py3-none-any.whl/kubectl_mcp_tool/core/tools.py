"""Core utilities for validating and working with Kubernetes commands.

This module provides core utilities for validating and working with Kubernetes commands,
including helper functions for command parsing and validation.
"""

import logging
import re
import shlex
from typing import Any, Dict, List, Optional, TypedDict, Union

from kubectl_mcp_tool.core.config import ALLOWED_UNIX_COMMANDS

logger = logging.getLogger(__name__)


class CommandResult(TypedDict, total=False):
    """Type structure for command execution results."""
    
    status: str  # "success" or "error"
    output: str  # Command output (stdout or stderr)
    exit_code: int  # Command exit code
    execution_time: float  # Command execution time in seconds
    error: Dict[str, Any]  # Error details if status is "error"


class ErrorDetails(TypedDict, total=False):
    """Type structure for error details."""
    
    message: str  # Error message
    code: str  # Error code
    details: Dict[str, Any]  # Additional error details


def is_pipe_command(command: str) -> bool:
    """Check if a command contains pipe operators.
    
    Args:
        command: Command string
        
    Returns:
        True if the command contains pipe operators, False otherwise
    """
    in_single_quote = False
    in_double_quote = False
    
    for char in command:
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif char == '|' and not in_single_quote and not in_double_quote:
            return True
    
    return False


def split_pipe_command(command: str) -> List[str]:
    """Split a command with pipe operators into individual commands.
    
    Args:
        command: Command string with pipe operators
        
    Returns:
        List of individual commands
    """
    commands = []
    current_command = ""
    in_single_quote = False
    in_double_quote = False
    
    for char in command:
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            current_command += char
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            current_command += char
        elif char == '|' and not in_single_quote and not in_double_quote:
            commands.append(current_command.strip())
            current_command = ""
        else:
            current_command += char
    
    if current_command.strip():
        commands.append(current_command.strip())
    
    return commands


def validate_unix_command(command: str) -> bool:
    """Validate a Unix command against the list of allowed commands.
    
    Args:
        command: Unix command string
        
    Returns:
        True if the command is allowed, False otherwise
    """
    try:
        parts = shlex.split(command)
        if not parts:
            return False
        
        command_name = parts[0]
        
        return command_name in ALLOWED_UNIX_COMMANDS
    except Exception as e:
        logger.error(f"Error validating Unix command: {e}")
        return False


def inject_context_namespace(command: str, context: Optional[str] = None, namespace: Optional[str] = None) -> str:
    """Inject context and namespace flags into a command if not already present.
    
    Args:
        command: Command string
        context: Kubernetes context
        namespace: Kubernetes namespace
        
    Returns:
        Command string with context and namespace flags
    """
    if not context and not namespace:
        return command
    
    try:
        parts = shlex.split(command)
        if not parts:
            return command
        
        has_context = any(arg.startswith("--context=") or arg == "--context" for arg in parts)
        has_namespace = any(arg.startswith("--namespace=") or arg.startswith("-n=") or arg == "--namespace" or arg == "-n" for arg in parts)
        
        if not has_context and context:
            parts.insert(1, f"--context={context}")
        
        if not has_namespace and namespace:
            insert_pos = 2 if not has_context and context else 1
            parts.insert(insert_pos, f"--namespace={namespace}")
        
        return shlex.join(parts)
    except Exception as e:
        logger.error(f"Error injecting context and namespace: {e}")
        return command
