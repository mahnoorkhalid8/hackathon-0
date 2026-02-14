"""
MCP Client Module
Handles communication with MCP servers for external actions.
"""

import yaml
import time
from pathlib import Path
from typing import Dict, Optional, Any


class MCPClient:
    """Client for MCP server communication."""

    def __init__(self, config_path: str = "./mcp/mcp_config.yaml"):
        # Load MCP configuration
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {'servers': {}, 'settings': {}}

        self.servers = self.config.get('servers', {})
        self.settings = self.config.get('settings', {})

    def call(self, server_name: str, action: str, params: Dict) -> Dict[str, Any]:
        """
        Call an MCP server.

        Args:
            server_name: Name of MCP server
            action: Action to perform
            params: Parameters for the action

        Returns:
            Response dictionary
        """
        # Check if server exists and is enabled
        if server_name not in self.servers:
            return {
                'success': False,
                'error': f'MCP server not found: {server_name}'
            }

        server = self.servers[server_name]
        if not server.get('enabled', False):
            return {
                'success': False,
                'error': f'MCP server disabled: {server_name}'
            }

        # Log call if enabled
        if self.settings.get('log_all_calls', True):
            print(f"[MCP] Calling {server_name}.{action}")

        # Simulate MCP call (in production, would make actual HTTP request)
        try:
            result = self._simulate_call(server_name, action, params)
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _simulate_call(self, server_name: str, action: str, params: Dict) -> Any:
        """
        Simulate MCP call for demonstration.

        In production, this would make actual HTTP requests to MCP servers.
        """
        time.sleep(0.5)  # Simulate network delay

        # Simulated responses
        if server_name == 'web_search':
            return {
                'query': params.get('query', ''),
                'results': [
                    {'title': 'Result 1', 'url': 'https://example.com/1'},
                    {'title': 'Result 2', 'url': 'https://example.com/2'}
                ]
            }
        elif server_name == 'api_caller':
            return {
                'status': 200,
                'response': {'message': 'API call successful'}
            }
        elif server_name == 'data_fetcher':
            return {
                'data': [1, 2, 3, 4, 5],
                'count': 5
            }

        return {'message': 'MCP call completed'}

    def list_servers(self) -> Dict[str, Dict]:
        """List all configured MCP servers."""
        return {
            name: {
                'enabled': server.get('enabled', False),
                'type': server.get('type', 'unknown'),
                'description': server.get('description', '')
            }
            for name, server in self.servers.items()
        }

    def is_enabled(self, server_name: str) -> bool:
        """Check if an MCP server is enabled."""
        return self.servers.get(server_name, {}).get('enabled', False)
