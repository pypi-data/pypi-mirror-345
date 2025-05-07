"""
Tool registry module for kubectl-mcp-tool.

This module provides an extensible tool framework for registering and managing
MCP tools for Kubernetes operations.
"""

import inspect
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Union, Set

logger = logging.getLogger(__name__)

class Tool:
    """Represents a tool in the MCP framework."""
    
    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable,
        schema: Optional[Dict[str, Any]] = None,
        required_params: Optional[Set[str]] = None,
        deprecated: bool = False,
        assistant_compatibility: Optional[List[str]] = None
    ):
        """Initialize a tool with its metadata and handler."""
        self.name = name
        self.description = description
        self.handler = handler
        self.schema = schema or self._generate_schema(handler)
        self.required_params = required_params or set()
        self.deprecated = deprecated
        self.assistant_compatibility = assistant_compatibility or ["claude", "cursor", "windsurf"]
    
    def _generate_schema(self, handler: Callable) -> Dict[str, Any]:
        """Generate a JSON schema for the tool based on the handler signature."""
        sig = inspect.signature(handler)
        parameters = {}
        
        for name, param in sig.parameters.items():
            if name == "self":
                continue
                
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == str:
                    param_type = "string"
                elif param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == dict or param.annotation == Dict:
                    param_type = "object"
                elif param.annotation == list or param.annotation == List:
                    param_type = "array"
            
            param_schema = {"type": param_type}
            if param.default != inspect.Parameter.empty:
                param_schema["default"] = param.default
            
            parameters[name] = param_schema
        
        return {
            "type": "object",
            "properties": parameters,
            "required": [
                name for name, param in sig.parameters.items()
                if param.default == inspect.Parameter.empty and name != "self"
            ]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.schema,
            "deprecated": self.deprecated
        }
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate that the required parameters are present."""
        for param in self.required_params:
            if param not in params:
                return False
        return True
    
    def is_compatible_with(self, assistant: str) -> bool:
        """Check if the tool is compatible with the given assistant."""
        return assistant.lower() in [a.lower() for a in self.assistant_compatibility]

class ToolRegistry:
    """Registry for MCP tools."""
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self.tools: Dict[str, Tool] = {}
    
    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable,
        schema: Optional[Dict[str, Any]] = None,
        required_params: Optional[Set[str]] = None,
        deprecated: bool = False,
        assistant_compatibility: Optional[List[str]] = None
    ) -> Tool:
        """Register a tool with the registry."""
        tool = Tool(
            name=name,
            description=description,
            handler=handler,
            schema=schema,
            required_params=required_params,
            deprecated=deprecated,
            assistant_compatibility=assistant_compatibility
        )
        self.tools[name] = tool
        logger.info(f"Registered tool: {name}")
        return tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self, assistant: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all registered tools, optionally filtered by assistant compatibility."""
        if assistant:
            return [
                tool.to_dict() for tool in self.tools.values()
                if tool.is_compatible_with(assistant)
            ]
        return [tool.to_dict() for tool in self.tools.values()]
    
    def call_tool(self, name: str, params: Dict[str, Any]) -> Any:
        """Call a tool with the given parameters."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        if not tool.validate_params(params):
            raise ValueError(f"Missing required parameters for tool: {name}")
        
        return tool.handler(**params)
    
    def register_function_as_tool(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        required_params: Optional[Set[str]] = None,
        deprecated: bool = False,
        assistant_compatibility: Optional[List[str]] = None
    ) -> Tool:
        """Register a function as a tool."""
        name = name or func.__name__
        description = description or func.__doc__ or f"Tool for {name}"
        
        return self.register_tool(
            name=name,
            description=description,
            handler=func,
            schema=schema,
            required_params=required_params,
            deprecated=deprecated,
            assistant_compatibility=assistant_compatibility
        )
    
    def tool_decorator(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        required_params: Optional[Set[str]] = None,
        deprecated: bool = False,
        assistant_compatibility: Optional[List[str]] = None
    ) -> Callable:
        """Decorator for registering a function as a tool."""
        def decorator(func: Callable) -> Callable:
            self.register_function_as_tool(
                func=func,
                name=name or func.__name__,
                description=description or func.__doc__,
                schema=schema,
                required_params=required_params,
                deprecated=deprecated,
                assistant_compatibility=assistant_compatibility
            )
            return func
        return decorator
