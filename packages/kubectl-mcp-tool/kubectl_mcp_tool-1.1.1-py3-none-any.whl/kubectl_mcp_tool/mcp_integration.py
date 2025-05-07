"""
MCP integration module for kubectl-mcp-tool.

This module provides the main integration point for the MCP server,
combining the transport layer, assistant integration, and tool registry
to create a complete MCP server for Kubernetes operations.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional, Union, Callable

from kubectl_mcp_tool.transport.transport_layer import (
    BaseTransport, StdioTransport, SSETransport, HTTPTransport, TransportFactory
)
from kubectl_mcp_tool.assistant_integration.assistant_adapter import (
    BaseAssistantAdapter, ClaudeAdapter, CursorAdapter, WindSurfAdapter,
    AssistantAdapterFactory, AssistantDetector
)
from kubectl_mcp_tool.tools.tool_registry import Tool, ToolRegistry

logger = logging.getLogger(__name__)

class MCPServer:
    """MCP server for Kubernetes operations."""
    
    def __init__(
        self,
        name: str,
        version: str,
        transport: BaseTransport,
        registry: Optional[ToolRegistry] = None,
        adapter: Optional[BaseAssistantAdapter] = None
    ):
        """Initialize the MCP server."""
        self.name = name
        self.version = version
        self.transport = transport
        self.registry = registry or ToolRegistry()
        self.adapter = adapter
        self.running = False
    
    async def start(self):
        """Start the MCP server."""
        self.running = True
        logger.info(f"Starting MCP server: {self.name} v{self.version}")
        
        while self.running:
            try:
                message = await self.transport.read_message()
                if not message:
                    continue
                
                if not self.adapter:
                    assistant_type = AssistantDetector.detect_assistant(message)
                    self.adapter = AssistantAdapterFactory.create_adapter(assistant_type)
                    logger.info(f"Detected assistant type: {assistant_type}")
                
                request = self.adapter.format_request(message)
                
                response = await self.process_request(request)
                
                response = self.adapter.format_response(response)
                
                await self.transport.write_message(response)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                try:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": message.get("id", "unknown"),
                        "error": {
                            "code": -32000,
                            "message": f"Internal server error: {str(e)}"
                        }
                    }
                    await self.transport.write_message(error_response)
                except Exception as e2:
                    logger.error(f"Error sending error response: {e2}")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an MCP request."""
        method = request.get("method", "")
        
        if method == "mcp.initialize":
            return await self.handle_initialize(request)
        elif method == "mcp.tool.call":
            return await self.handle_tool_call(request)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", "unknown"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP initialization request."""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id", "unknown"),
            "result": {
                "name": self.name,
                "version": self.version,
                "tools": self.registry.list_tools()
            }
        }
    
    async def handle_tool_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP tool call request."""
        params = request.get("params", {})
        tool_name = params.get("name", "")
        tool_input = params.get("input", {})
        
        try:
            tool = self.registry.get_tool(tool_name)
            if not tool:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id", "unknown"),
                    "error": {
                        "code": -32602,
                        "message": f"Tool not found: {tool_name}"
                    }
                }
            
            result = self.registry.call_tool(tool_name, tool_input)
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", "unknown"),
                "result": result
            }
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", "unknown"),
                "error": {
                    "code": -32000,
                    "message": f"Error calling tool {tool_name}: {str(e)}"
                }
            }
    
    async def stop(self):
        """Stop the MCP server."""
        self.running = False
        await self.transport.close()
        logger.info(f"Stopped MCP server: {self.name} v{self.version}")

class MCPServerBuilder:
    """Builder for creating MCP servers."""
    
    def __init__(self, name: str, version: str):
        """Initialize the builder with the server name and version."""
        self.name = name
        self.version = version
        self.transport = None
        self.registry = ToolRegistry()
        self.adapter = None
    
    def with_transport(self, transport_type: str, **kwargs) -> 'MCPServerBuilder':
        """Set the transport for the server."""
        self.transport = TransportFactory.create_transport(transport_type, **kwargs)
        return self
    
    def with_assistant(self, assistant_type: str) -> 'MCPServerBuilder':
        """Set the assistant adapter for the server."""
        self.adapter = AssistantAdapterFactory.create_adapter(assistant_type)
        return self
    
    def with_tool(
        self,
        name: str,
        description: str,
        handler: Callable,
        schema: Optional[Dict[str, Any]] = None,
        required_params: Optional[set] = None,
        deprecated: bool = False,
        assistant_compatibility: Optional[List[str]] = None
    ) -> 'MCPServerBuilder':
        """Add a tool to the server's registry."""
        self.registry.register_tool(
            name=name,
            description=description,
            handler=handler,
            schema=schema,
            required_params=required_params,
            deprecated=deprecated,
            assistant_compatibility=assistant_compatibility
        )
        return self
    
    def build(self) -> MCPServer:
        """Build the MCP server."""
        if not self.transport:
            raise ValueError("Transport not specified")
        
        return MCPServer(
            name=self.name,
            version=self.version,
            transport=self.transport,
            registry=self.registry,
            adapter=self.adapter
        )

async def run_server(server: MCPServer):
    """Run an MCP server."""
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, stopping server")
        await server.stop()
    except Exception as e:
        logger.error(f"Error running server: {e}")
        await server.stop()
        raise

def main():
    """Main entry point for the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    import argparse
    parser = argparse.ArgumentParser(description="MCP server for Kubernetes operations")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="Transport protocol to use"
    )
    parser.add_argument(
        "--assistant",
        choices=["claude", "cursor", "windsurf"],
        help="Assistant type to use"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to for HTTP transport"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for HTTP transport"
    )
    parser.add_argument(
        "--sse-url",
        help="URL for SSE transport"
    )
    args = parser.parse_args()
    
    builder = MCPServerBuilder(
        name="kubectl-mcp-tool",
        version="0.1.0"
    )
    
    if args.transport == "stdio":
        builder.with_transport("stdio")
    elif args.transport == "sse":
        if not args.sse_url:
            parser.error("--sse-url is required for SSE transport")
        builder.with_transport("sse", url=args.sse_url)
    elif args.transport == "http":
        builder.with_transport("http", host=args.host, port=args.port)
    
    if args.assistant:
        builder.with_assistant(args.assistant)
    
    server = builder.build()
    
    asyncio.run(run_server(server))

if __name__ == "__main__":
    main()
