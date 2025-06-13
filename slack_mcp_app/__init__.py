"""
Slack MCP App Package
Professional Slack automation tools for MCP.
"""

from .slack_mcp_server import mcp
from . import tools

__all__ = ["mcp", "tools"]
