"""
Assistant integration module for kubectl-mcp-tool.

This module provides adapters for integrating with different AI assistants,
ensuring compatibility with Claude, Cursor, WindSurf, and other MCP-compatible
assistants.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional, Union, Callable

logger = logging.getLogger(__name__)

class BaseAssistantAdapter:
    """Base class for all assistant adapters."""
    
    def __init__(self, name: str):
        """Initialize the adapter with the assistant name."""
        self.name = name
    
    def format_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Format a request for the specific assistant."""
        return request
    
    def format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format a response for the specific assistant."""
        return response
    
    def parse_natural_language_query(self, query: str) -> Dict[str, Any]:
        """Parse a natural language query from the assistant."""
        return {"query": query}

class ClaudeAdapter(BaseAssistantAdapter):
    """Adapter for Claude AI assistant."""
    
    def __init__(self):
        """Initialize the Claude adapter."""
        super().__init__("Claude")
    
    def format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format a response for Claude."""
        if "result" in response:
            result = response["result"]
            
            if "output" in result:
                return response
            
            formatted_result = {
                "output": [
                    {
                        "type": "text",
                        "text": self._format_text_output(result)
                    }
                ]
            }
            
            return {
                "jsonrpc": response.get("jsonrpc", "2.0"),
                "id": response.get("id", "1"),
                "result": formatted_result
            }
        
        return response
    
    def _format_text_output(self, result: Dict[str, Any]) -> str:
        """Format the result as text for Claude."""
        if isinstance(result, str):
            return result
        
        command = result.get("command", "")
        command_result = result.get("result", "")
        
        output = f"Command: {command}\n\nResult:\n"
        if command_result:
            output += command_result
        else:
            output += "Command completed successfully with no output"
        
        return output

class CursorAdapter(BaseAssistantAdapter):
    """Adapter for Cursor AI assistant."""
    
    def __init__(self):
        """Initialize the Cursor adapter."""
        super().__init__("Cursor")
    
    def format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format a response for Cursor."""
        return response

class WindSurfAdapter(BaseAssistantAdapter):
    """Adapter for WindSurf AI assistant."""
    
    def __init__(self):
        """Initialize the WindSurf adapter."""
        super().__init__("WindSurf")
    
    def format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format a response for WindSurf."""
        return response

class AssistantAdapterFactory:
    """Factory for creating assistant adapters."""
    
    @staticmethod
    def create_adapter(assistant_type: str) -> BaseAssistantAdapter:
        """Create an adapter for the specified assistant type."""
        assistant_type = assistant_type.lower()
        
        if assistant_type == "claude":
            return ClaudeAdapter()
        elif assistant_type == "cursor":
            return CursorAdapter()
        elif assistant_type == "windsurf":
            return WindSurfAdapter()
        else:
            logger.warning(f"Unknown assistant type: {assistant_type}, using default adapter")
            return BaseAssistantAdapter(assistant_type)

class AssistantDetector:
    """Utility for detecting the assistant type from requests."""
    
    @staticmethod
    def detect_assistant(request: Dict[str, Any]) -> str:
        """Detect the assistant type from the request format."""
        if "claude" in str(request).lower():
            return "claude"
        
        if "cursor" in str(request).lower():
            return "cursor"
        
        if "windsurf" in str(request).lower():
            return "windsurf"
        
        return "generic"
