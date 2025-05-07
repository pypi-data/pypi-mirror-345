#!/usr/bin/env python3
"""
Natural language processing for kubectl.
This module parses natural language queries and converts them to kubectl commands.
"""

import re
import subprocess
import logging
import os
import json
import shlex
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("natural-language")

def process_query(query: str, args: List[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Process a natural language query and convert it to a kubectl command.
    
    Args:
        query: The natural language query to process
        args: Optional list of args to pass to kubectl
        kwargs: Optional additional keyword arguments
        
    Returns:
        A dictionary containing the kubectl command and its output
    """
    try:
        logger.info(f"Processing query: {query}")
        logger.info(f"With args: {args}")
        logger.info(f"With kwargs: {kwargs}")
        
        # Try to parse the query and generate a kubectl command
        command = parse_query(query, args)
        
        # Log the generated command
        logger.info(f"Generated kubectl command: {command}")
        
        intent = "unknown"
        resource_type = "unknown"
        
        for op in ["get", "describe", "create", "delete", "apply", "scale", "logs", "exec", "port-forward", "top", "explain"]:
            if op in command:
                intent = op
                break
        
        for res in ["pods", "deployments", "services", "nodes", "namespaces", "configmaps", "secrets", "statefulsets", "ingresses"]:
            if res in command:
                resource_type = res
                break
        
        # Execute the command
        try:
            result = execute_command(command)
            success = True
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            result = f"Error executing command: {str(e)}"
            success = False
        
        formatted_output = None
        try:
            from .utils.terminal_output import format_status, format_header, format_table
            
            if resource_type == "pods" and success:
                from .utils.terminal_output import format_pod_list
                try:
                    pod_data = []
                    lines = result.strip().split('\n')
                    if len(lines) > 1:  # Skip header
                        for line in lines[1:]:
                            parts = re.split(r'\s+', line.strip(), maxsplit=5)
                            if len(parts) >= 5:
                                name, ready, status, restarts, age = parts[:5]
                                ready_parts = ready.split('/')
                                ready_containers = int(ready_parts[0]) if len(ready_parts) > 0 and ready_parts[0].isdigit() else 0
                                total_containers = int(ready_parts[1]) if len(ready_parts) > 1 and ready_parts[1].isdigit() else 1
                                pod_data.append({
                                    "name": name,
                                    "namespace": extract_namespace(query) or "default",
                                    "status": status,
                                    "ready_containers": ready_containers,
                                    "total_containers": total_containers,
                                    "restarts": int(restarts) if restarts.isdigit() else 0,
                                    "age": age
                                })
                    formatted_output = format_pod_list(pod_data) if pod_data else None
                except Exception as e:
                    logger.error(f"Error formatting pod list: {e}")
            
            elif resource_type == "namespaces" and success:
                from .utils.terminal_output import format_namespace_list
                try:
                    namespace_data = []
                    lines = result.strip().split('\n')
                    if len(lines) > 1:  # Skip header
                        for line in lines[1:]:
                            parts = re.split(r'\s+', line.strip(), maxsplit=2)
                            if len(parts) >= 2:
                                name, status = parts[:2]
                                age = parts[2] if len(parts) > 2 else "unknown"
                                namespace_data.append({
                                    "name": name,
                                    "status": status,
                                    "age": age
                                })
                    formatted_output = format_namespace_list(namespace_data) if namespace_data else None
                except Exception as e:
                    logger.error(f"Error formatting namespace list: {e}")
                    
            elif resource_type == "deployments" and success:
                from .utils.terminal_output import format_deployment_list
                try:
                    deployment_data = []
                    lines = result.strip().split('\n')
                    if len(lines) > 1:  # Skip header
                        for line in lines[1:]:
                            parts = re.split(r'\s+', line.strip(), maxsplit=5)
                            if len(parts) >= 5:
                                name, ready, up_to_date, available, age = parts[:5]
                                ready_parts = ready.split('/')
                                ready_replicas = int(ready_parts[0]) if len(ready_parts) > 0 and ready_parts[0].isdigit() else 0
                                replicas = int(ready_parts[1]) if len(ready_parts) > 1 and ready_parts[1].isdigit() else 0
                                deployment_data.append({
                                    "name": name,
                                    "namespace": extract_namespace(query) or "default",
                                    "ready_replicas": ready_replicas,
                                    "replicas": replicas,
                                    "updated_replicas": int(up_to_date) if up_to_date.isdigit() else 0,
                                    "available_replicas": int(available) if available.isdigit() else 0,
                                    "age": age
                                })
                    formatted_output = format_deployment_list(deployment_data) if deployment_data else None
                except Exception as e:
                    logger.error(f"Error formatting deployment list: {e}")
                    
            elif resource_type == "services" and success:
                from .utils.terminal_output import format_service_list
                try:
                    service_data = []
                    lines = result.strip().split('\n')
                    if len(lines) > 1:  # Skip header
                        for line in lines[1:]:
                            parts = re.split(r'\s+', line.strip(), maxsplit=6)
                            if len(parts) >= 5:
                                name, type_val, cluster_ip, external_ip = parts[:4]
                                ports = parts[4] if len(parts) > 4 else ""
                                age = parts[5] if len(parts) > 5 else "unknown"
                                
                                ports_list = []
                                for port_str in ports.split(','):
                                    if '/' in port_str:
                                        port, protocol = port_str.split('/')
                                        ports_list.append({"port": port.strip(), "protocol": protocol.strip()})
                                
                                service_data.append({
                                    "name": name,
                                    "namespace": extract_namespace(query) or "default",
                                    "type": type_val,
                                    "cluster_ip": cluster_ip,
                                    "external_ip": external_ip,
                                    "ports": ports_list,
                                    "age": age
                                })
                    formatted_output = format_service_list(service_data) if service_data else None
                except Exception as e:
                    logger.error(f"Error formatting service list: {e}")
                    
            
            
        except ImportError:
            logger.debug("Terminal output utilities not available for colored formatting")
        except Exception as e:
            logger.error(f"Error applying colored formatting: {e}")
            
        return {
            "command": command,
            "result": result,
            "success": success,
            "intent": intent,
            "resource_type": resource_type,
            "kubernetes_command": command,
            "formatted_output": formatted_output
        }
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {
            "command": "",
            "result": f"Error processing query: {str(e)}",
            "success": False,
            "intent": "error",
            "resource_type": "unknown",
            "kubernetes_command": ""
        }

def parse_query(query: str, args: List[str] = None) -> str:
    """
    Parse a natural language query and convert it to a kubectl command.
    
    Args:
        query: The natural language query to parse
        args: Optional list of args to append to the kubectl command
        
    Returns:
        The kubectl command to execute
    """
    # Normalize the query
    query = query.lower().strip()
    
    if "get pod logs for" in query:
        pod_logs_match = re.search(r"get\s+pod\s+logs\s+for\s+(\w+[-\w]*)", query)
        if pod_logs_match:
            pod_name = pod_logs_match.group(1)
            namespace = extract_namespace(query)
            if namespace:
                return f"kubectl logs {pod_name} -n {namespace}"
            else:
                return f"kubectl logs {pod_name}"
    
    if re.search(r"(get|list|show|display|show\s+me)\s+(all\s+)?pod(s)?", query) and "logs" not in query and "log" not in query:
        try:
            namespace = extract_namespace(query)
            if namespace:
                return f"kubectl get pods -n {namespace}"
            else:
                return "kubectl get pods"
        except Exception as e:
            logger.error(f"Error extracting namespace: {e}")
            return "kubectl get pods"
    
    if re.search(r"(get|list|show|display)\s+all(\s+resources)?", query):
        namespace = extract_namespace(query)
        if namespace:
            return f"kubectl get all -n {namespace}"
        else:
            return "kubectl get all"
    
    if re.search(r"(get|list|show|display)\s+(all\s+)?deployment(s)?", query):
        namespace = extract_namespace(query)
        if namespace:
            return f"kubectl get deployments -n {namespace}"
        else:
            return "kubectl get deployments"
    
    if re.search(r"(get|list|show|display)\s+(all\s+)?service(s)?", query):
        namespace = extract_namespace(query)
        if namespace:
            return f"kubectl get services -n {namespace}"
        else:
            return "kubectl get services"
    
    if re.search(r"(get|list|show|display)\s+(all\s+)?node(s)?", query):
        return "kubectl get nodes"
    
    if re.search(r"(get|list|show|display)\s+(all\s+)?namespace(s)?", query):
        return "kubectl get namespaces"
    
    if re.search(r"(get|list|show|display)\s+(all\s+)?configmap(s)?", query):
        namespace = extract_namespace(query)
        if namespace:
            return f"kubectl get configmaps -n {namespace}"
        else:
            return "kubectl get configmaps"
    
    if re.search(r"(get|list|show|display)\s+(all\s+)?secret(s)?", query):
        namespace = extract_namespace(query)
        if namespace:
            return f"kubectl get secrets -n {namespace}"
        else:
            return "kubectl get secrets"
    
    if re.search(r"describe\s+(\w+)", query):
        match = re.search(r"describe\s+(\w+)\s+(\w+[-\w]*)", query)
        if match:
            resource_type = match.group(1)
            resource_name = match.group(2)
            namespace = extract_namespace(query)
            if namespace:
                return f"kubectl describe {resource_type} {resource_name} -n {namespace}"
            else:
                return f"kubectl describe {resource_type} {resource_name}"
        else:
            resource_match = re.search(r"describe\s+(\w+)", query)
            if resource_match:
                resource_type = resource_match.group(1)
                namespace = extract_namespace(query)
                if namespace:
                    return f"kubectl describe {resource_type} -n {namespace}"
                else:
                    return f"kubectl describe {resource_type}"
    
    if "get pod logs for" in query:
        pod_logs_match = re.search(r"get\s+pod\s+logs\s+for\s+(\w+[-\w]*)", query)
        if pod_logs_match:
            pod_name = pod_logs_match.group(1)
            namespace = extract_namespace(query)
            if namespace:
                return f"kubectl logs {pod_name} -n {namespace}"
            else:
                return f"kubectl logs {pod_name}"
    
    if re.search(r"(logs|log|get\s+logs)", query):
        pod_name = extract_pod_name(query)
        namespace = extract_namespace(query)
        if pod_name and namespace:
            return f"kubectl logs {pod_name} -n {namespace}"
        elif pod_name:
            return f"kubectl logs {pod_name}"
        else:
            name_patterns = [
                r"(logs|log)\s+(?:of|from|for)?\s+(\w+[-\w]*)",
                r"get\s+pod\s+logs\s+(?:of|from|for)?\s+(\w+[-\w]*)",
                r"get\s+logs\s+(?:of|from|for)?\s+(\w+[-\w]*)",
                r"pod\s+logs\s+(?:of|from|for)?\s+(\w+[-\w]*)"
            ]
            
            for pattern in name_patterns:
                name_match = re.search(pattern, query)
                if name_match:
                    if len(name_match.groups()) > 1:
                        resource_name = name_match.group(2)
                    else:
                        resource_name = name_match.group(1)
                    
                    if namespace:
                        return f"kubectl logs {resource_name} -n {namespace}"
                    else:
                        return f"kubectl logs {resource_name}"
            
            if "pod logs" in query or "logs" in query or "log" in query:
                for prep in ["for", "from", "of"]:
                    prep_match = re.search(fr"{prep}\s+(\w+[-\w]*)", query)
                    if prep_match:
                        pod_name = prep_match.group(1)
                        if namespace:
                            return f"kubectl logs {pod_name} -n {namespace}"
                        else:
                            return f"kubectl logs {pod_name}"
            
            return "kubectl logs"
    
    if re.search(r"(create|apply)", query):
        if "deployment" in query:
            match = re.search(r"(create|apply)\s+deployment\s+(\w+[-\w]*)", query)
            if match:
                deployment_name = match.group(2)
                replicas = re.search(r"(\d+)\s+replica", query)
                replicas_count = replicas.group(1) if replicas else "1"
                namespace = extract_namespace(query)
                image_match = re.search(r"(image|with)\s+([a-zA-Z0-9/\-:.]+)", query)
                image = image_match.group(2) if image_match else "nginx:latest"
                
                if namespace:
                    return f"kubectl create deployment {deployment_name} --image={image} --replicas={replicas_count} -n {namespace}"
                else:
                    return f"kubectl create deployment {deployment_name} --image={image} --replicas={replicas_count}"
        elif "namespace" in query:
            match = re.search(r"(create|apply)\s+namespace\s+(\w+[-\w]*)", query)
            if match:
                namespace_name = match.group(2)
                return f"kubectl create namespace {namespace_name}"
    
    if re.search(r"scale", query):
        if "deployment" in query:
            match = re.search(r"scale\s+deployment\s+(\w+[-\w]*)", query)
            if match:
                deployment_name = match.group(1)
                replicas = re.search(r"to\s+(\d+)", query)
                replicas_count = replicas.group(1) if replicas else "1"
                namespace = extract_namespace(query)
                
                if namespace:
                    return f"kubectl scale deployment {deployment_name} --replicas={replicas_count} -n {namespace}"
                else:
                    return f"kubectl scale deployment {deployment_name} --replicas={replicas_count}"
        elif "statefulset" in query:
            match = re.search(r"scale\s+statefulset\s+(\w+[-\w]*)", query)
            if match:
                statefulset_name = match.group(1)
                replicas = re.search(r"to\s+(\d+)", query)
                replicas_count = replicas.group(1) if replicas else "1"
                namespace = extract_namespace(query)
                
                if namespace:
                    return f"kubectl scale statefulset {statefulset_name} --replicas={replicas_count} -n {namespace}"
                else:
                    return f"kubectl scale statefulset {statefulset_name} --replicas={replicas_count}"
    
    if re.search(r"(delete|remove)", query):
        resource_match = re.search(r"(delete|remove)\s+(\w+)\s+(\w+[-\w]*)", query)
        if resource_match:
            resource_type = resource_match.group(2)
            resource_name = resource_match.group(3)
            namespace = extract_namespace(query)
            
            if namespace:
                return f"kubectl delete {resource_type} {resource_name} -n {namespace}"
            else:
                return f"kubectl delete {resource_type} {resource_name}"
    
    if re.search(r"port[\s-]forward", query):
        pod_match = re.search(r"port[\s-]forward\s+(?:to)?\s+(\w+[-\w]*)", query)
        if pod_match:
            pod_name = pod_match.group(1)
            port_match = re.search(r"port\s+(\d+)(?:\s+to\s+(\d+))?", query)
            local_port = port_match.group(1) if port_match else "8080"
            remote_port = port_match.group(2) if port_match and port_match.group(2) else local_port
            namespace = extract_namespace(query)
            
            if namespace:
                return f"kubectl port-forward {pod_name} {local_port}:{remote_port} -n {namespace}"
            else:
                return f"kubectl port-forward {pod_name} {local_port}:{remote_port}"
    
    if re.search(r"exec", query):
        pod_match = re.search(r"exec\s+(?:into)?\s+(\w+[-\w]*)", query)
        if pod_match:
            pod_name = pod_match.group(1)
            command_match = re.search(r"(?:with|using|command)\s+([\"'].*?[\"']|\S+)", query)
            command = command_match.group(1) if command_match else "/bin/sh"
            namespace = extract_namespace(query)
            
            if namespace:
                return f"kubectl exec -it {pod_name} -n {namespace} -- {command}"
            else:
                return f"kubectl exec -it {pod_name} -- {command}"
    
    if re.search(r"(switch|use|change)\s+(context|cluster)", query):
        context_match = re.search(r"(switch|use|change)\s+(context|cluster)\s+(?:to)?\s+(\w+[-\w]*)", query)
        if context_match:
            context_name = context_match.group(3)
            return f"kubectl config use-context {context_name}"
    
    if re.search(r"(switch|use|change)\s+namespace", query):
        namespace_match = re.search(r"(switch|use|change)\s+namespace\s+(?:to)?\s+(\w+[-\w]*)", query)
        if namespace_match:
            namespace = namespace_match.group(2)
            return f"kubectl config set-context --current --namespace={namespace}"
    
    if re.search(r"explain", query):
        resource_match = re.search(r"explain\s+(\w+)", query)
        if resource_match:
            resource_type = resource_match.group(1)
            return f"kubectl explain {resource_type}"
    
    if re.search(r"api[\s-]resources", query):
        return "kubectl api-resources"
    
    if re.search(r"top", query):
        if "node" in query:
            return "kubectl top nodes"
        elif "pod" in query:
            namespace = extract_namespace(query)
            if namespace:
                return f"kubectl top pods -n {namespace}"
            else:
                return "kubectl top pods"
    
    resource_types = ["pod", "deployment", "service", "node", "namespace", "configmap", "secret", "ingress"]
    operations = ["get", "describe", "create", "delete", "apply", "scale", "logs", "exec"]
    
    for operation in operations:
        if operation in query:
            for resource in resource_types:
                if resource in query:
                    namespace = extract_namespace(query)
                    if namespace:
                        return f"kubectl {operation} {resource} -n {namespace}"
                    else:
                        return f"kubectl {operation} {resource}"
    
    if re.search(r"show\s+me\s+(all\s+)?(\w+)", query):
        resource_match = re.search(r"show\s+me\s+(all\s+)?(\w+)", query)
        if resource_match:
            resource = resource_match.group(2)
            namespace = extract_namespace(query)
            if namespace:
                return f"kubectl get {resource} -n {namespace}"
            else:
                return f"kubectl get {resource}"

    cmd = query
    for phrase in ["please", "can you", "i want to", "show me", "tell me about", "what are", "how many"]:
        cmd = cmd.replace(phrase, "")
    
    cmd = cmd.strip()
    if cmd and not cmd.startswith("kubectl"):
        cmd = "kubectl get " + cmd  # Default to "get" operation
    
    if args and len(args) > 0:
        cmd = f"{cmd} {' '.join(args)}"
    
    return cmd or "kubectl get all"

def extract_namespace(query: str) -> Optional[str]:
    """
    Extract namespace from a query.
    
    Args:
        query: The query to extract the namespace from
        
    Returns:
        The namespace or None if not found
    """
    namespace_patterns = [
        r"(?:in|from|namespace|ns)\s+(\w+[-\w]*)",
        r"--namespace[=\s]+(\w+[-\w]*)",
        r"-n\s+(\w+[-\w]*)",
        r"namespace[=\s]+(\w+[-\w]*)"
    ]
    
    for pattern in namespace_patterns:
        namespace_match = re.search(pattern, query)
        if namespace_match:
            return namespace_match.group(1)
    return None

def extract_pod_name(query: str) -> Optional[str]:
    """
    Extract pod name from a query.
    
    Args:
        query: The query to extract the pod name from
        
    Returns:
        The pod name or None if not found
    """
    pod_patterns = [
        r"pod\s+(\w+[-\w]*)",
        r"pod\s+named\s+(\w+[-\w]*)",
        r"pod\s+called\s+(\w+[-\w]*)",
        r"pod/(\w+[-\w]*)"
    ]
    
    for pattern in pod_patterns:
        pod_match = re.search(pattern, query)
        if pod_match:
            return pod_match.group(1)
    
    name_match = re.search(r"(get|describe|delete|logs)\s+pod\s+(\w+[-\w]*)", query)
    if name_match:
        return name_match.group(2)
    
    return None

def execute_command(command: str, **kwargs) -> str:
    """
    Execute a kubectl command and return the output.
    
    Args:
        command: The kubectl command to execute
        kwargs: Optional additional keyword arguments
        
    Returns:
        The command output
    """
    try:
        # For enhanced safety, handle the case where kubeconfig doesn't exist
        kubeconfig = os.environ.get('KUBECONFIG', os.path.expanduser('~/.kube/config'))
        if not os.path.exists(kubeconfig):
            logger.warning(f"Kubeconfig not found at {kubeconfig}")
            return f"Warning: Kubernetes config not found at {kubeconfig}. Please configure kubectl."
        
        env = os.environ.copy()
        if "GOOGLE_APPLICATION_CREDENTIALS" in env and "USE_GKE_GCLOUD_AUTH_PLUGIN" not in env:
            env["USE_GKE_GCLOUD_AUTH_PLUGIN"] = "True"
            logger.info("Enabled GKE authentication plugin")
        
        if not command.startswith("kubectl"):
            command = f"kubectl {command}"
            logger.debug(f"Added kubectl prefix to command: {command}")
        
        try:
            args = shlex.split(command)
            shell_mode = False
        except Exception as e:
            logger.warning(f"Could not split command, falling back to shell mode: {e}")
            args = command
            shell_mode = True
        
        subprocess_kwargs = {
            'shell': shell_mode,
            'check': False,  # Don't raise exception on non-zero exit
            'capture_output': True,
            'text': True,
            'timeout': kwargs.get('timeout', 30),  # Use provided timeout or default to 30
            'env': env
        }
        
        result = subprocess.run(args, **subprocess_kwargs)
        
        # Check for errors
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            logger.warning(f"Command failed with exit code {result.returncode}: {error_msg}")
            
            formatted_error = f"Command failed: {error_msg}\n\nCommand: {command}"
            
            if "not found" in error_msg and "command not found" in error_msg:
                formatted_error += "\n\nSuggestion: kubectl may not be installed or not in your PATH."
            elif "Unable to connect to the server" in error_msg:
                formatted_error += "\n\nSuggestion: Check your Kubernetes cluster connection or VPN."
            elif "forbidden" in error_msg.lower() or "unauthorized" in error_msg.lower():
                formatted_error += "\n\nSuggestion: You may not have sufficient permissions for this operation."
            elif "gke-gcloud-auth-plugin" in error_msg:
                formatted_error += "\n\nSuggestion: Install the GKE authentication plugin with 'gcloud components install gke-gcloud-auth-plugin'."
            
            return formatted_error
        
        output = result.stdout.strip() if result.stdout else "Command completed successfully with no output"
        
        try:
            from .utils.terminal_output import format_command_output
            formatted_output = format_command_output(command, output)
            if formatted_output:
                return formatted_output
        except ImportError:
            logger.debug("Terminal output formatting not available")
        except Exception as e:
            logger.error(f"Error formatting output: {e}")
        
        if len(output.splitlines()) > 20:
            line_count = len(output.splitlines())
            output = f"Command returned {line_count} lines of output:\n\n{output}"
        
        return output
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {command}")
        return "Command timed out after 30 seconds. The operation may still be running in the cluster."
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return f"Error: {str(e)}\n\nCommand: {command}"
