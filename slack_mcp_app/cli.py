#!/usr/bin/env python3
"""
CLI interface for Slack MCP Server.

This module provides a command-line interface for running and managing
the Slack MCP server with various configuration options.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import structlog
import uvicorn
from fastapi import FastAPI

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class ConfigurationError(Exception):
    """Raised when there's an error in configuration."""
    pass


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def load_config(config_path: Optional[Path] = None) -> dict:
    """Load configuration from JSON file or environment variables."""
    config = {}
    
    # Try to load from config file
    if config_path and config_path.exists():
        try:
            with open(config_path) as f:
                file_config = json.load(f)
                # Extract runtime environment variables if present
                if "ImageRepository" in file_config:
                    config = file_config["ImageRepository"]["ImageConfiguration"]["RuntimeEnvironmentVariables"]
                else:
                    config = file_config
        except (json.JSONDecodeError, KeyError) as e:
            raise ConfigurationError(f"Invalid configuration file: {e}")
    
    # Override with environment variables
    env_vars = {
        "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
        "SLACK_SIGNING_SECRET": os.getenv("SLACK_SIGNING_SECRET"),
        "SLACK_USER_TOKEN": os.getenv("SLACK_USER_TOKEN"),
        "FASTMCP_PORT": os.getenv("FASTMCP_PORT", "8000"),
        "FASTMCP_HOST": os.getenv("FASTMCP_HOST", "127.0.0.1"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
        "ENABLE_METRICS": os.getenv("ENABLE_METRICS", "false"),
        "RATE_LIMIT_ENABLED": os.getenv("RATE_LIMIT_ENABLED", "true"),
        "RATE_LIMIT_REQUESTS_PER_MINUTE": os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"),
    }
    
    # Only include non-None values
    for key, value in env_vars.items():
        if value is not None:
            config[key] = value
    
    return config


def validate_config(config: dict) -> None:
    """Validate required configuration parameters."""
    required_vars = ["SLACK_BOT_TOKEN"]
    missing_vars = [var for var in required_vars if not config.get(var)]
    
    if missing_vars:
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    # Validate bot token format
    bot_token = config.get("SLACK_BOT_TOKEN")
    if not bot_token.startswith("xoxb-"):
        logger.warning("SLACK_BOT_TOKEN does not appear to be a valid bot token")


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Slack MCP Server - Professional FastMCP server for Slack automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run with default settings
  %(prog)s --port 8080              # Run on port 8080
  %(prog)s --host 0.0.0.0           # Bind to all interfaces
  %(prog)s --config env.json        # Use specific config file
  %(prog)s --log-level DEBUG        # Enable debug logging
  %(prog)s --reload                 # Enable auto-reload for development
        """,
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)",
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file (JSON format)",
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development (not recommended for production)",
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)",
    )
    
    parser.add_argument(
        "--transport",
        choices=["streamable-http", "stdio"],
        default="streamable-http",
        help="MCP transport protocol (default: streamable-http)",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )
    
    return parser


def run_server(
    host: str,
    port: int,
    log_level: str,
    reload: bool = False,
    workers: int = 1,
    transport: str = "streamable-http",
) -> None:
    """Run the Slack MCP server."""
    if transport == "stdio":
        # For stdio transport, import and run directly
        from slack_mcp_app.slack_mcp_server import mcp
        mcp.run(transport="stdio")
    else:
        # For HTTP transport, use uvicorn
        uvicorn.run(
            "slack_mcp_app.slack_mcp_server:mcp",
            host=host,
            port=port,
            log_level=log_level.lower(),
            reload=reload,
            workers=workers if not reload else 1,  # Reload doesn't work with multiple workers
            access_log=True,
            server_header=False,  # Security: don't expose server info
            date_header=False,    # Security: don't expose date
        )


def check_health() -> bool:
    """Check if the server is healthy."""
    import httpx
    
    try:
        response = httpx.get("http://127.0.0.1:8000/health", timeout=5.0)
        return response.status_code == 200
    except httpx.RequestError:
        return False


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Setup logging
        setup_logging(args.log_level)
        
        # Load and validate configuration
        config = load_config(args.config)
        validate_config(config)
        
        # Set environment variables from config
        os.environ.update(config)
        
        # Override with CLI arguments
        host = args.host or config.get("FASTMCP_HOST", "127.0.0.1")
        port = args.port or int(config.get("FASTMCP_PORT", "8000"))
        
        logger.info(
            "Starting Slack MCP Server",
            host=host,
            port=port,
            transport=args.transport,
            log_level=args.log_level,
            reload=args.reload,
            workers=args.workers,
            environment=config.get("ENVIRONMENT", "development"),
        )
        
        # Run the server
        run_server(
            host=host,
            port=port,
            log_level=args.log_level,
            reload=args.reload,
            workers=args.workers,
            transport=args.transport,
        )
        
        return 0
        
    except ConfigurationError as e:
        logger.error("Configuration error", error=str(e))
        return 1
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        return 0
    except Exception as e:
        logger.error("Unexpected error", error=str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 