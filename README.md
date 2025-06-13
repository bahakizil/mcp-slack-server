# Slack MCP Server

This repository contains a **FastMCP** server that exposes a handful of
Slack automations (posting messages, reacting, …) as **MCP tools** so that
LLM agents, Claude Desktop, LiteLLM or any other MCP-compatible client can
interact with your company Slack workspace in a safe, auditable way.

## Features

* `list_channels`   – List public channels the bot can access
* `post_message`    – Send a plain-text message to a channel
* `reply_to_thread` – Reply inside an existing thread
* `add_reaction`    – React to a specific message with an emoji

All calls are executed through the official `slack_sdk` and require a
**bot token** with the corresponding permissions (`channels:read`,
`chat:write`, `reactions:write`).

## Production Deployment

🌐 **Live Production Server**: `https://qg7p6udte6.us-east-1.awsapprunner.com/mcp`

The server is deployed on AWS App Runner and ready for use with MCP clients like Cursor.

### Team Setup - Connecting from Cursor

**For your team members:** Add this to your Cursor MCP configuration (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "slack-fastmcp-aws": {
      "transport": "http",
      "url": "https://qg7p6udte6.us-east-1.awsapprunner.com/mcp/"
    }
  }
}
```

**Quick Setup Script for Team:**
```bash
#!/bin/bash
echo "🔧 Slack MCP kurulumu başlıyor..."

# Create Cursor config directory
mkdir -p ~/.cursor

# Backup existing config
if [ -f ~/.cursor/mcp.json ]; then
    cp ~/.cursor/mcp.json ~/.cursor/mcp.json.backup
    echo "📦 Mevcut config yedeklendi"
fi

# Add Slack MCP config
cat >> ~/.cursor/mcp.json << 'EOF'
{
  "mcpServers": {
    "slack-fastmcp-aws": {
      "transport": "http",
      "url": "https://qg7p6udte6.us-east-1.awsapprunner.com/mcp/"
    }
  }
}
EOF

echo "✅ Slack MCP konfigürasyonu hazır!"
echo "🔄 Cursor'u yeniden başlat ve Tools sekmesinden 'slack-fastmcp-aws' enable et"
echo "🎯 29 Slack tool'u kullanılabilir olacak!"
```

**Manual Setup:**
1. Create/edit `~/.cursor/mcp.json` file
2. Add the JSON configuration above
3. Restart Cursor completely
4. Go to Tools tab and enable `slack-fastmcp-aws`
5. You should see 29 Slack tools available! 🎉

**Features for Team:**
- ✅ **Multi-user Support**: Everyone can connect simultaneously
- ✅ **Centralized Server**: Single AWS endpoint for the whole team
- ✅ **29 Slack Tools**: Full Slack workspace automation
- ✅ **Real-time**: Instant messaging, reactions, and channel management

## Local Development

```bash
# 1. Clone / install dependencies
conda env create -f environment.yml
conda activate slack-mcp

# 2. Set up environment variables in env.json
# Required: SLACK_BOT_TOKEN
# Optional: SLACK_SIGNING_SECRET, FASTMCP_PORT

# 3. Run the server locally
python run_server.py        # Starts on http://127.0.0.1:8000

# 4. Test with example client
export MCP_URL=http://127.0.0.1:8000/mcp
python example_client.py
```

## AWS Deployment

```bash
# 1. Build and deploy to App Runner
chmod +x deploy.sh
./deploy.sh

# 2. Monitor deployment
aws apprunner describe-service --service-arn <service-arn>
```

## Environment Variables

* `SLACK_BOT_TOKEN` (required) - Your Slack bot token (xoxb-...)
* `SLACK_SIGNING_SECRET` (optional) - Slack signing secret for validation
* `FASTMCP_PORT` (optional) - Server port, defaults to 8000
* `PORT` (AWS App Runner) - Container port for cloud deployment

## Slack Bot Setup

1. Create a Slack app at https://api.slack.com/apps
2. Enable bot features and install to workspace
3. Get bot token from "OAuth & Permissions"
4. Required scopes: `channels:read`, `chat:write`, `reactions:write`

## Tools Available

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_channels` | List public channels | `limit` (optional, default: 100) |
| `post_message` | Send message to channel | `channel_id`, `text` |
| `reply_to_thread` | Reply to thread | `channel_id`, `thread_ts`, `text` |
| `add_reaction` | Add emoji reaction | `channel_id`, `timestamp`, `reaction` |

## Testing

Test the production server:
```bash
npx -y @modelcontextprotocol/inspector https://qg7p6udte6.us-east-1.awsapprunner.com/mcp
```

Health check:
```bash
curl https://qg7p6udte6.us-east-1.awsapprunner.com/health
```

## Quick start

```bash
# 1. Clone / install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Provide your Slack credentials
export SLACK_BOT_TOKEN="xoxb-…"

# 3. Run the server (Streamable HTTP on :8000 by default)
python -m mcp.slack_mcp_server  # or   uv run mcp.slack_mcp_server
```

The server is now reachable at `http://127.0.0.1:8000/mcp`. Point any MCP
client to this URL and call the tools just like any other FastMCP server.

### Using Claude Desktop / Inspector

```bash
npx -y @modelcontextprotocol/inspector http://127.0.0.1:8000/mcp
```

Inspect the live schema, test tools and monitor traffic.

## Production deployment

* **Docker** – Build an image from the project root:
  ```Dockerfile
  FROM python:3.12-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY mcp/ ./mcp
  CMD ["python", "-m", "mcp.slack_mcp_server"]
  ```
* **Systemd + uvicorn** – If you prefer an ASGI process manager.

Ensure the `SLACK_BOT_TOKEN` environment variable is present in the
runtime environment.

## Extending the server

This is merely a starting point – add as many tools, resources and prompts
as your workflows require. FastMCP's decorator syntax makes it trivial to
expose additional Slack endpoints or even third-party services under the
same MCP server.

Happy hacking! 🎉 