"""
MCP Server Wrapper

This module provides a wrapper for stdio-based MCP servers
to run on AWS Lambda and integrate with AgentCore Gateway.
"""

import asyncio
import json
import logging
import subprocess
import tempfile
import os
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)


class McpServerWrapper:
    """
    Wrapper for stdio-based MCP servers to run on Lambda.
    
    This class manages the lifecycle of stdio-based MCP servers,
    handling process management and communication.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the MCP server wrapper.
        
        Args:
            config: Configuration dictionary containing command, args, and env
        """
        self.config = config
        self.process = None
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=1)
        
    def _ensure_server_running(self) -> subprocess.Popen:
        """Ensure the MCP server process is running."""
        with self.lock:
            if self.process is None or self.process.poll() is not None:
                logger.info("Starting MCP server process")
                
                # Prepare environment
                env = os.environ.copy()
                env.update(self.config.get("env", {}))
                
                # Start the process
                cmd = [self.config["command"]] + self.config.get("args", [])
                logger.info(f"Starting command: {' '.join(cmd)}")
                
                self.process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True,
                    bufsize=0
                )
                
                logger.info(f"MCP server process started with PID: {self.process.pid}")
                
        return self.process
    
    def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a request to the MCP server and get the response.
        
        Args:
            request: MCP request dictionary
            
        Returns:
            MCP response dictionary
        """
        process = self._ensure_server_running()
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            logger.debug(f"Sending request: {request_json.strip()}")
            
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Read response
            response_line = process.stdout.readline()
            if not response_line:
                raise RuntimeError("No response from MCP server")
                
            logger.debug(f"Received response: {response_line.strip()}")
            
            response = json.loads(response_line.strip())
            return response
            
        except Exception as e:
            logger.error(f"Error communicating with MCP server: {str(e)}")
            # Kill the process if there's an error
            if self.process:
                self.process.terminate()
                self.process = None
            raise
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP request by forwarding it to the wrapped server.
        
        Args:
            request: MCP request dictionary
            
        Returns:
            MCP response dictionary
        """
        try:
            logger.info(f"Handling MCP request: {request.get('method', 'unknown')}")
            
            # Forward the request to the actual MCP server
            response = self._send_request(request)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
    
    def cleanup(self):
        """Clean up the MCP server process."""
        with self.lock:
            if self.process:
                logger.info("Terminating MCP server process")
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Force killing MCP server process")
                    self.process.kill()
                self.process = None
    
    def __del__(self):
        """Cleanup when the wrapper is destroyed."""
        self.cleanup()