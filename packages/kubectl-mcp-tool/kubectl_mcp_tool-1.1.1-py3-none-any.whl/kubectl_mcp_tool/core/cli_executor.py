"""CLI Executor for Kubernetes MCP Tool.

This module provides utilities for executing Kubernetes CLI commands
with proper validation, error handling, timeouts, and output processing.
"""

import asyncio
import logging
import os
import re
import shlex
import signal
import subprocess
from typing import Any, Dict, Optional, Tuple, Union

from kubectl_mcp_tool.core.tools import CommandResult
from kubectl_mcp_tool.core.security_validation import validate_command
from kubectl_mcp_tool.core.config import (
    DEFAULT_TIMEOUT,
    MAX_OUTPUT_SIZE,
    SUPPORTED_CLI_TOOLS,
)
from kubectl_mcp_tool.core.errors import (
    AuthenticationError,
    CommandExecutionError,
    CommandTimeoutError,
    CommandValidationError,
    create_error_result,
)

logger = logging.getLogger(__name__)


async def check_cli_installed(cli_tool: str) -> bool:
    """Check if a CLI tool is installed and available on the system.

    Args:
        cli_tool: Name of the CLI tool to check (e.g., kubectl, istioctl)

    Returns:
        True if the CLI tool is installed, False otherwise
    """
    if cli_tool not in SUPPORTED_CLI_TOOLS:
        logger.warning(f"Unsupported CLI tool: {cli_tool}")
        return False

    check_command = SUPPORTED_CLI_TOOLS[cli_tool]["check_command"]
    
    try:
        process = await asyncio.create_subprocess_shell(
            check_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            logger.info(f"{cli_tool} is installed. Version: {stdout.decode().strip()}")
            return True
        else:
            logger.warning(f"{cli_tool} check failed. stderr: {stderr.decode().strip()}")
            return False
    except Exception as e:
        logger.error(f"Error checking if {cli_tool} is installed: {e}")
        return False


async def execute_command(command: str, timeout: int = DEFAULT_TIMEOUT) -> CommandResult:
    """Execute a Kubernetes CLI command with validation, timeout, and error handling.

    Args:
        command: The full command to execute (can include pipes)
        timeout: Timeout in seconds

    Returns:
        CommandResult containing output and status

    Raises:
        CommandValidationError: If the command fails validation
        CommandExecutionError: If the command execution fails
        CommandTimeoutError: If the command times out
        AuthenticationError: If authentication fails
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        await validate_command(command)
    except CommandValidationError as e:
        logger.warning(f"Command validation failed: {e}")
        raise

    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            
            message = f"Command timed out after {timeout} seconds: {command}"
            logger.warning(message)
            raise CommandTimeoutError(message, {"command": command, "timeout": timeout})

        execution_time = asyncio.get_event_loop().time() - start_time
        
        stderr_str = stderr.decode("utf-8", errors="replace")
        if any(auth_err in stderr_str for auth_err in [
            "Unauthorized", "Authorization failed", "authentication required",
            "unable to connect to the server", "error: You must be logged in"
        ]):
            message = f"Authentication error: {stderr_str.strip()}"
            logger.warning(message)
            raise AuthenticationError(message, {"command": command})

        stdout_str = stdout.decode("utf-8", errors="replace")
        
        if len(stdout_str) > MAX_OUTPUT_SIZE:
            truncated_message = f"\n... [Output truncated, total length: {len(stdout_str)} characters] ..."
            stdout_str = stdout_str[:MAX_OUTPUT_SIZE] + truncated_message
            logger.info(f"Output truncated for command: {command}")
        
        if process.returncode != 0:
            message = f"Command failed with exit code {process.returncode}: {stderr_str.strip()}"
            logger.warning(message)
            
            return CommandResult(
                status="error",
                output=stderr_str if stderr_str else stdout_str,
                exit_code=process.returncode,
                execution_time=execution_time,
                error={
                    "message": message,
                    "code": "EXECUTION_ERROR",
                    "details": {
                        "command": command,
                        "exit_code": process.returncode,
                        "stderr": stderr_str
                    }
                }
            )
        
        logger.info(f"Command executed successfully: {command}")
        return CommandResult(
            status="success",
            output=stdout_str,
            exit_code=process.returncode,
            execution_time=execution_time
        )
    except (CommandValidationError, CommandTimeoutError, AuthenticationError):
        raise
    except Exception as e:
        message = f"Error executing command: {e}"
        logger.error(message)
        raise CommandExecutionError(message, {"command": command})


async def get_command_help(cli_tool: str, command: Optional[str] = None) -> Dict[str, Any]:
    """Get help information for a CLI command.

    Args:
        cli_tool: The CLI tool to get help for (kubectl, istioctl, helm, argocd)
        command: Optional specific command to get help for

    Returns:
        Dictionary with help text and status
    """
    if cli_tool not in SUPPORTED_CLI_TOOLS:
        message = f"Unsupported CLI tool: {cli_tool}"
        logger.warning(message)
        return {
            "help_text": message,
            "status": "error",
            "error": {
                "message": message,
                "code": "UNSUPPORTED_TOOL"
            }
        }

    help_command = SUPPORTED_CLI_TOOLS[cli_tool]["help_command"]
    
    if command:
        help_command = f"{help_command} {command}"

    try:
        result = await execute_command(help_command)
        return {
            "help_text": result["output"],
            "status": result["status"]
        }
    except Exception as e:
        message = f"Error getting help for {cli_tool} {command or ''}: {e}"
        logger.error(message)
        return {
            "help_text": message,
            "status": "error",
            "error": {
                "message": message,
                "code": "HELP_ERROR"
            }
        }
