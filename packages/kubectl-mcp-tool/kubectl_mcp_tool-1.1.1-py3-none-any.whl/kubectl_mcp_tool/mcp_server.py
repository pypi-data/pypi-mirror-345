#!/usr/bin/env python3
"""
MCP server implementation for kubectl-mcp-tool.
"""

import json
import sys
import logging
import asyncio
import os
import shutil
from typing import Dict, Any, List, Optional, Callable, Awaitable

def find_python_executable():
    """
    Find an available Python executable.
    
    This function checks common Python paths and returns the first one that exists.
    Used to resolve the "spawn python ENOENT" error in Claude Desktop.
    """
    logger = logging.getLogger("mcp-server")
    
    python_paths = [
        "python3",                       # System default Python 3
        "python",                        # System default Python
        "/usr/bin/python3",              # Common Linux path
        "/usr/local/bin/python3",        # Common macOS/Homebrew path
        "/usr/bin/python",               # Fallback Linux path
        "/usr/local/bin/python",         # Fallback macOS path
        os.path.expanduser("~/.pyenv/shims/python3"),  # pyenv path
        os.path.expanduser("~/.pyenv/shims/python"),   # pyenv fallback
    ]
    
    for path in python_paths:
        try:
            resolved_path = shutil.which(path)
            if resolved_path:
                logger.info(f"Found Python at: {resolved_path}")
                return resolved_path
        except Exception as e:
            logger.debug(f"Error checking Python path {path}: {e}")
    
    logger.error("Could not find a valid Python executable")
    return "python3"  # Default to python3 as a last resort

try:
    from .utils.terminal_output import (
        format_pod_list, format_deployment_list, format_service_list,
        format_namespace_list, format_status, format_header
    )
    COLORED_OUTPUT = True
except ImportError:
    COLORED_OUTPUT = False
    logging.warning("Terminal output utilities not found. Using plain text output.")

try:
    from .fastmcp_wrapper import FastMCP
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        logging.error("MCP SDK not found. Installing...")
        import subprocess
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "mcp>=1.5.0"
            ])
            try:
                from .fastmcp_wrapper import FastMCP
            except ImportError:
                from mcp.server.fastmcp import FastMCP
        except Exception as e:
            logging.error(f"Failed to install MCP SDK: {e}")
            raise

from .natural_language import process_query

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mcp-server")

PYTHON_EXECUTABLE = find_python_executable()
logger.info(f"Using Python executable: {PYTHON_EXECUTABLE}")

class MCPServer:
    """MCP server implementation."""
    
    def __init__(self, name: str):
        """Initialize the MCP server."""
        self.name = name
        # Create a new server instance using the FastMCP API
        self.server = FastMCP(name=name)
        
        # Register tools using the new FastMCP API
        self.setup_tools()
        
    def _calculate_age(self, timestamp):
        """Calculate age from timestamp."""
        if not timestamp:
            return "unknown"
            
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        creation_time = timestamp
        
        diff = now - creation_time
        
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"
    
    def setup_tools(self):
        """Set up the tools for the MCP server."""
        
        @self.server.tool()
        def process_natural_language(query: str, args: List[str] = None) -> Dict[str, Any]:
            """Process natural language query for kubectl."""
            try:
                logger.info(f"Received query: {query}")
                logger.info(f"Received args: {args}")
                result = process_query(query)
                return {"success": True, "result": result}
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def get_pods(namespace: Optional[str] = None) -> Dict[str, Any]:
            """Get all pods in the specified namespace."""
            try:
                from kubernetes import client, config
                config.load_kube_config()
                v1 = client.CoreV1Api()
                
                if namespace:
                    pods = v1.list_namespaced_pod(namespace)
                else:
                    pods = v1.list_pod_for_all_namespaces()
                
                pod_list = [
                    {
                        "name": pod.metadata.name,
                        "namespace": pod.metadata.namespace,
                        "status": pod.status.phase,
                        "ip": pod.status.pod_ip,
                        "ready_containers": sum(1 for c in pod.status.container_statuses if c.ready) if pod.status.container_statuses else 0,
                        "total_containers": len(pod.status.container_statuses) if pod.status.container_statuses else 1,
                        "restarts": sum(c.restart_count for c in pod.status.container_statuses) if pod.status.container_statuses else 0,
                        "age": self._calculate_age(pod.metadata.creation_timestamp) if pod.metadata.creation_timestamp else "unknown"
                    }
                    for pod in pods.items
                ]
                
                formatted_output = format_pod_list(pod_list) if COLORED_OUTPUT else None
                
                return {
                    "success": True,
                    "pods": pod_list,
                    "formatted_output": formatted_output
                }
            except Exception as e:
                logger.error(f"Error getting pods: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def get_namespaces() -> Dict[str, Any]:
            """Get all Kubernetes namespaces."""
            try:
                from kubernetes import client, config
                config.load_kube_config()
                v1 = client.CoreV1Api()
                
                namespaces = v1.list_namespace()
                
                namespace_list = [
                    {
                        "name": ns.metadata.name,
                        "status": ns.status.phase,
                        "age": self._calculate_age(ns.metadata.creation_timestamp) if ns.metadata.creation_timestamp else "unknown"
                    }
                    for ns in namespaces.items
                ]
                
                formatted_output = format_namespace_list(namespace_list) if COLORED_OUTPUT else None
                
                return {
                    "success": True,
                    "namespaces": namespace_list,
                    "formatted_output": formatted_output
                }
            except Exception as e:
                logger.error(f"Error getting namespaces: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def create_deployment(name: str, image: str, replicas: int, namespace: Optional[str] = "default") -> Dict[str, Any]:
            """Create a new deployment."""
            try:
                from kubernetes import client, config
                config.load_kube_config()
                apps_v1 = client.AppsV1Api()
                
                deployment = client.V1Deployment(
                    metadata=client.V1ObjectMeta(name=name),
                    spec=client.V1DeploymentSpec(
                        replicas=replicas,
                        selector=client.V1LabelSelector(
                            match_labels={"app": name}
                        ),
                        template=client.V1PodTemplateSpec(
                            metadata=client.V1ObjectMeta(
                                labels={"app": name}
                            ),
                            spec=client.V1PodSpec(
                                containers=[
                                    client.V1Container(
                                        name=name,
                                        image=image
                                    )
                                ]
                            )
                        )
                    )
                )
                
                apps_v1.create_namespaced_deployment(
                    body=deployment,
                    namespace=namespace
                )
                
                return {
                    "success": True,
                    "message": f"Deployment {name} created successfully"
                }
            except Exception as e:
                logger.error(f"Error creating deployment: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def delete_resource(resource_type: str, name: str, namespace: Optional[str] = "default") -> Dict[str, Any]:
            """Delete a Kubernetes resource."""
            try:
                from kubernetes import client, config
                config.load_kube_config()
                
                if resource_type == "pod":
                    v1 = client.CoreV1Api()
                    v1.delete_namespaced_pod(name=name, namespace=namespace)
                elif resource_type == "deployment":
                    apps_v1 = client.AppsV1Api()
                    apps_v1.delete_namespaced_deployment(name=name, namespace=namespace)
                elif resource_type == "service":
                    v1 = client.CoreV1Api()
                    v1.delete_namespaced_service(name=name, namespace=namespace)
                else:
                    return {"success": False, "error": f"Unsupported resource type: {resource_type}"}
                
                return {
                    "success": True,
                    "message": f"{resource_type} {name} deleted successfully"
                }
            except Exception as e:
                logger.error(f"Error deleting resource: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def get_logs(pod_name: str, namespace: Optional[str] = "default", container: Optional[str] = None, tail: Optional[int] = None) -> Dict[str, Any]:
            """Get logs from a pod."""
            try:
                from kubernetes import client, config
                config.load_kube_config()
                v1 = client.CoreV1Api()
                
                logs = v1.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    container=container,
                    tail_lines=tail
                )
                
                return {
                    "success": True,
                    "logs": logs
                }
            except Exception as e:
                logger.error(f"Error getting logs: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def port_forward(pod_name: str, local_port: int, pod_port: int, namespace: Optional[str] = "default") -> Dict[str, Any]:
            """Forward local port to pod port."""
            try:
                import subprocess
                
                cmd = [
                    "kubectl", "port-forward",
                    f"pod/{pod_name}",
                    f"{local_port}:{pod_port}",
                    "-n", namespace
                ]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                return {
                    "success": True,
                    "message": f"Port forwarding started: localhost:{local_port} -> {pod_name}:{pod_port}",
                    "process_pid": process.pid
                }
            except Exception as e:
                logger.error(f"Error setting up port forward: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def scale_deployment(name: str, replicas: int, namespace: Optional[str] = "default") -> Dict[str, Any]:
            """Scale a deployment."""
            try:
                from kubernetes import client, config
                config.load_kube_config()
                apps_v1 = client.AppsV1Api()
                
                # Get the deployment
                deployment = apps_v1.read_namespaced_deployment(
                    name=name,
                    namespace=namespace
                )
                
                # Update replicas
                deployment.spec.replicas = replicas
                
                # Apply the update
                apps_v1.patch_namespaced_deployment(
                    name=name,
                    namespace=namespace,
                    body=deployment
                )
                
                return {
                    "success": True,
                    "message": f"Deployment {name} scaled to {replicas} replicas"
                }
            except Exception as e:
                logger.error(f"Error scaling deployment: {e}")
                return {"success": False, "error": str(e)}
    
    async def serve_stdio(self):
        """Serve the MCP server over stdio transport."""
        # Add detailed logging for debugging Cursor integration
        logger.info("Starting MCP server with stdio transport")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"System Python executable: {sys.executable}")
        logger.info(f"Detected Python executable: {PYTHON_EXECUTABLE}")
        logger.info(f"Python version: {sys.version}")
        
        # Log Kubernetes configuration
        kube_config = os.environ.get('KUBECONFIG', '~/.kube/config')
        expanded_path = os.path.expanduser(kube_config)
        logger.info(f"KUBECONFIG: {kube_config} (expanded: {expanded_path})")
        if os.path.exists(expanded_path):
            logger.info(f"Kubernetes config file exists at {expanded_path}")
        else:
            logger.warning(f"Kubernetes config file does not exist at {expanded_path}")
        
        # Continue with normal server startup
        await self.server.run_stdio_async()
    
    async def serve_sse(self, port: int):
        """Serve the MCP server over SSE transport."""
        logger.info(f"Starting MCP server with SSE transport on port {port}")
        await self.server.run_sse_async(port=port)
        
    @staticmethod
    def generate_claude_desktop_config(output_path=None):
        """
        Generate a Claude Desktop configuration file with the correct Python path.
        
        This helps resolve the "spawn python ENOENT" error by providing the full path
        to the Python executable.
        
        Args:
            output_path: Optional path to write the config file. If None, just returns the config.
            
        Returns:
            The configuration as a dictionary.
        """
        python_path = PYTHON_EXECUTABLE
        
        config = {
            "mcpServers": {
                "kubernetes": {
                    "command": python_path,
                    "args": [
                        "-m",
                        "kubectl_mcp_tool.minimal_wrapper"
                    ],
                    "env": {
                        "KUBECONFIG": os.path.expanduser("~/.kube/config"),
                        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"),
                        "PYTHONPATH": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "MCP_DEBUG": "1"
                    }
                }
            }
        }
        
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Claude Desktop configuration written to {output_path}")
        
        return config
        
    async def serve_sse(self, port: int):
        """Serve the MCP server over SSE transport."""
        logger.info(f"Starting MCP server with SSE transport on port {port}")
        await self.server.run_sse_async(port=port)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server for kubectl")
    parser.add_argument("--generate-config", action="store_true", help="Generate Claude Desktop configuration")
    parser.add_argument("--output", help="Output path for Claude Desktop configuration")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    if args.generate_config:
        output_path = args.output or os.path.expanduser("~/.config/Claude/claude_desktop_config.json")
        MCPServer.generate_claude_desktop_config(output_path)
        print(f"Claude Desktop configuration generated at: {output_path}")
        sys.exit(0)
    
    print("Use --generate-config to create a Claude Desktop configuration")
