"""
Transport layer module for kubectl-mcp-tool.

This module provides transport protocol implementations for the MCP server,
supporting multiple transport protocols (stdio, SSE, HTTP).
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional, Callable, Union, AsyncGenerator
import aiohttp
from aiohttp import web
import sseclient

logger = logging.getLogger(__name__)

class BaseTransport:
    """Base class for all transport protocols."""
    
    async def read_message(self) -> Optional[Dict[str, Any]]:
        """Read a message from the transport."""
        raise NotImplementedError("Subclasses must implement read_message")
    
    async def write_message(self, message: Dict[str, Any]) -> None:
        """Write a message to the transport."""
        raise NotImplementedError("Subclasses must implement write_message")
    
    async def close(self) -> None:
        """Close the transport."""
        pass

class StdioTransport(BaseTransport):
    """Transport implementation using standard input/output."""
    
    def __init__(self, input_stream=None, output_stream=None):
        """Initialize the transport with optional custom streams."""
        self.input_stream = input_stream or sys.stdin
        self.output_stream = output_stream or sys.stdout
        self.buffer = ""
        self.message_queue = asyncio.Queue()
        self._setup_input_reader()
    
    def _setup_input_reader(self):
        """Set up the input reader task."""
        if hasattr(self.input_stream, 'buffer'):
            loop = asyncio.get_event_loop()
            loop.add_reader(self.input_stream, self._read_stdin_callback)
    
    def _read_stdin_callback(self):
        """Callback for reading from stdin."""
        try:
            data = self.input_stream.readline()
            if data:
                asyncio.create_task(self._process_input(data))
        except Exception as e:
            logger.error(f"Error reading from stdin: {e}")
    
    async def _process_input(self, data: str):
        """Process input data and add complete messages to the queue."""
        self.buffer += data
        
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            if line.strip():
                try:
                    message = json.loads(line)
                    await self.message_queue.put(message)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
    
    async def read_message(self) -> Optional[Dict[str, Any]]:
        """Read a message from the input stream."""
        if not hasattr(self.input_stream, 'buffer'):
            try:
                line = self.input_stream.readline()
                if not line:
                    return None
                return json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                return None
        
        return await self.message_queue.get()
    
    async def write_message(self, message: Dict[str, Any]) -> None:
        """Write a message to the output stream."""
        try:
            json_str = json.dumps(message)
            self.output_stream.write(json_str + '\n')
            self.output_stream.flush()
        except Exception as e:
            logger.error(f"Error writing to stdout: {e}")

class SSETransport(BaseTransport):
    """Transport implementation using Server-Sent Events (SSE)."""
    
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        """Initialize the SSE transport with the given URL and headers."""
        self.url = url
        self.headers = headers or {}
        self.client = None
        self.message_queue = asyncio.Queue()
        self.running = False
        self.session = None
    
    async def start(self):
        """Start the SSE client."""
        self.running = True
        self.session = aiohttp.ClientSession()
        asyncio.create_task(self._listen_for_events())
    
    async def _listen_for_events(self):
        """Listen for SSE events."""
        try:
            async with self.session.get(self.url, headers=self.headers) as response:
                if response.status != 200:
                    logger.error(f"Failed to connect to SSE endpoint: {response.status}")
                    return
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        try:
                            message = json.loads(data)
                            await self.message_queue.put(message)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse SSE data: {e}")
        except Exception as e:
            logger.error(f"Error in SSE connection: {e}")
        finally:
            self.running = False
    
    async def read_message(self) -> Optional[Dict[str, Any]]:
        """Read a message from the SSE stream."""
        if not self.running:
            await self.start()
        
        return await self.message_queue.get()
    
    async def write_message(self, message: Dict[str, Any]) -> None:
        """Write a message to the SSE client (not typically used for SSE)."""
        logger.warning("SSE transport does not support writing messages")
    
    async def close(self) -> None:
        """Close the SSE transport."""
        self.running = False
        if self.session:
            await self.session.close()

class HTTPTransport(BaseTransport):
    """Transport implementation using HTTP."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """Initialize the HTTP transport with the given host and port."""
        self.host = host
        self.port = port
        self.app = web.Application()
        self.app.router.add_post('/mcp', self._handle_request)
        self.runner = None
        self.site = None
        self.message_queue = asyncio.Queue()
        self.response_queues = {}
    
    async def start(self):
        """Start the HTTP server."""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        logger.info(f"HTTP transport listening on http://{self.host}:{self.port}/mcp")
    
    async def _handle_request(self, request):
        """Handle incoming HTTP requests."""
        try:
            data = await request.json()
            request_id = data.get('id')
            
            await self.message_queue.put(data)
            
            response_queue = asyncio.Queue()
            self.response_queues[request_id] = response_queue
            
            response = await response_queue.get()
            del self.response_queues[request_id]
            
            return web.json_response(response)
        except Exception as e:
            logger.error(f"Error handling HTTP request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def read_message(self) -> Optional[Dict[str, Any]]:
        """Read a message from the HTTP request queue."""
        return await self.message_queue.get()
    
    async def write_message(self, message: Dict[str, Any]) -> None:
        """Write a message to the appropriate response queue."""
        request_id = message.get('id')
        if request_id in self.response_queues:
            await self.response_queues[request_id].put(message)
        else:
            logger.warning(f"No response queue for request ID: {request_id}")
    
    async def close(self) -> None:
        """Close the HTTP transport."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

class TransportFactory:
    """Factory for creating transport instances."""
    
    @staticmethod
    def create_transport(transport_type: str, **kwargs) -> BaseTransport:
        """Create a transport instance of the specified type."""
        if transport_type == "stdio":
            return StdioTransport(**kwargs)
        elif transport_type == "sse":
            return SSETransport(**kwargs)
        elif transport_type == "http":
            return HTTPTransport(**kwargs)
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")
