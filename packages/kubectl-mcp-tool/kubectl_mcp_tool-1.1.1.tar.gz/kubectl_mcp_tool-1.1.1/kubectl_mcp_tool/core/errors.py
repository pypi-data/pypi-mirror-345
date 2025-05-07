"""Standardized error handling for Kubernetes MCP Tool.

This module provides standardized error handling for the Kubernetes MCP Tool,
including exception classes and helper functions for creating structured error responses.
"""

from typing import Any, Dict, Optional


class K8sMCPError(Exception):
    """Base exception class for Kubernetes MCP Tool errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.code = "K8S_MCP_ERROR"


class CommandValidationError(K8sMCPError):
    """Exception raised when a command fails validation."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, details)
        self.code = "COMMAND_VALIDATION_ERROR"


class CommandExecutionError(K8sMCPError):
    """Exception raised when a command execution fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, details)
        self.code = "COMMAND_EXECUTION_ERROR"


class AuthenticationError(K8sMCPError):
    """Exception raised when authentication fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, details)
        self.code = "AUTHENTICATION_ERROR"


class CommandTimeoutError(K8sMCPError):
    """Exception raised when a command times out."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, details)
        self.code = "COMMAND_TIMEOUT_ERROR"


def create_error_result(
    command: str,
    error: Exception,
    exit_code: Optional[int] = None,
    stderr: Optional[str] = None
) -> Dict[str, Any]:
    """Create a structured error result.

    Args:
        command: The command that failed
        error: The exception that was raised
        exit_code: Optional exit code from the command
        stderr: Optional stderr output from the command

    Returns:
        Dictionary with error details
    """
    if isinstance(error, K8sMCPError):
        error_code = error.code
        error_details = error.details
    else:
        error_code = "UNKNOWN_ERROR"
        error_details = {}

    result = {
        "status": "error",
        "output": str(error),
        "error": {
            "message": str(error),
            "code": error_code,
            "details": {
                "command": command,
                **error_details
            }
        }
    }

    if exit_code is not None:
        result["exit_code"] = exit_code
        result["error"]["details"]["exit_code"] = exit_code

    if stderr:
        result["error"]["details"]["stderr"] = stderr

    return result
