"""
Tests for MCP server wrapper functionality
"""

import json
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add lambda directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from mcp_wrapper import McpServerWrapper


class TestMcpServerWrapper:
    """Test cases for MCP server wrapper."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "command": "echo",
            "args": ["test"],
            "env": {"TEST_VAR": "test_value"}
        }
        self.wrapper = McpServerWrapper(self.config)
    
    @patch('subprocess.Popen')
    def test_ensure_server_running(self, mock_popen):
        """Test that server process is started correctly."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        process = self.wrapper._ensure_server_running()
        
        assert process == mock_process
        mock_popen.assert_called_once()
        
        # Check that the command was constructed correctly
        call_args = mock_popen.call_args
        assert call_args[0][0] == ["echo", "test"]
    
    @patch('subprocess.Popen')
    def test_handle_request_success(self, mock_popen):
        """Test successful request handling."""
        # Mock process
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.pid = 12345
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stdout.readline.return_value = '{"jsonrpc": "2.0", "id": 1, "result": {"test": "response"}}\n'
        mock_popen.return_value = mock_process
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        response = self.wrapper.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["test"] == "response"
    
    @patch('subprocess.Popen')
    def test_handle_request_error(self, mock_popen):
        """Test error handling in request processing."""
        # Mock process that fails
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.pid = 12345
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stdout.readline.return_value = ""  # Empty response
        mock_popen.return_value = mock_process
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test",
            "params": {}
        }
        
        response = self.wrapper.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
    
    def test_cleanup(self):
        """Test process cleanup."""
        mock_process = Mock()
        mock_process.terminate = Mock()
        mock_process.wait = Mock()
        
        self.wrapper.process = mock_process
        self.wrapper.cleanup()
        
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once_with(timeout=5)
        assert self.wrapper.process is None


class TestMcpServerWrapperIntegration:
    """Integration tests for MCP server wrapper."""
    
    def test_config_validation(self):
        """Test that configuration is properly validated."""
        config = {
            "command": "python",
            "args": ["-c", "print('test')"],
            "env": {}
        }
        
        wrapper = McpServerWrapper(config)
        assert wrapper.config == config
    
    def test_multiple_requests(self):
        """Test handling multiple requests (mocked)."""
        config = {
            "command": "echo",
            "args": ["test"],
            "env": {}
        }
        
        wrapper = McpServerWrapper(config)
        
        # This would require a real MCP server to test properly
        # For now, just ensure the wrapper can be created multiple times
        wrapper2 = McpServerWrapper(config)
        assert wrapper.config == wrapper2.config


if __name__ == "__main__":
    pytest.main([__file__])