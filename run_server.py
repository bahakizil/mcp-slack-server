import json
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_JSON = BASE_DIR / "env.json"

if not ENV_JSON.exists():
    sys.exit("env.json not found. Please provide environment configuration.")

config = json.loads(ENV_JSON.read_text())
vars_ = (
    config.get("ImageRepository", {})
    .get("ImageConfiguration", {})
    .get("RuntimeEnvironmentVariables", {})
)

if not vars_:
    sys.exit("RuntimeEnvironmentVariables not present in env.json")

os.environ.update(vars_)

# Set port from environment variable for App Runner
port = os.getenv("PORT", "8000")
os.environ["FASTMCP_PORT"] = port
os.environ["FASTMCP_HOST"] = "0.0.0.0"  # Bind to all interfaces for App Runner

print("[run_server] Exported env variables:")
for k in vars_:
    print(f"  {k}=****")
print(f"  PORT={port}")
print(f"  FASTMCP_HOST=0.0.0.0")

# Import and run the server directly - FastMCP will use FASTMCP_PORT env var
try:
    print("[run_server] Starting Slack MCP Server...")
    from slack_mcp_app.slack_mcp_server import mcp
    
    # Health check endpoints are already added in slack_mcp_server.py
    print("[run_server] Health check endpoints pre-configured")
    
    # FastMCP.run() uses FASTMCP_PORT and FASTMCP_HOST environment variables automatically
    mcp.run(transport="streamable-http", host="0.0.0.0", port=int(port))
except Exception as e:
    print(f"[run_server] Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 