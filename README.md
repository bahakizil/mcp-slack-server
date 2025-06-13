# 🚀 Professional MCP Slack Server

Enterprise-grade **Model Context Protocol (MCP)** server for comprehensive Slack workspace automation. Built with **FastMCP**, **AWS deployment**, and **29+ powerful tools** for team collaboration.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-1.0+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

### 📧 **Message Management**
- Send messages to channels
- Reply to threads
- Search messages across workspace
- Delete and edit messages
- Schedule messages for later

### 👥 **Channel & User Management**
- List channels and users
- Create and archive channels
- Join/leave channels
- Set channel topics and descriptions
- User status management

### 📎 **File Operations**
- Upload files to channels
- List and manage workspace files
- Delete files with permissions

### 🎭 **Reactions & Interactions**
- Add/remove emoji reactions
- Pin/unpin important messages
- Custom emoji management

### ⏰ **Automation**
- Create reminders
- Conversation history analysis
- Real-time notifications
- Thread management

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Slack App** with appropriate permissions
- **AWS Account** (for cloud deployment)
- **Git**

### 1. Clone Repository

```bash
git clone https://github.com/bahakizil/mcp-slack-server.git
cd mcp-slack-server
```

### 2. Create Slack App

1. Go to [Slack API Console](https://api.slack.com/apps)
2. Create new app "From scratch"
3. Name: `MCP Slack Server` 
4. Choose your workspace

#### Required OAuth Scopes:

**Bot Token Scopes:**
```
channels:read, channels:write, channels:history
chat:write, chat:write.public
files:read, files:write
reactions:read, reactions:write
users:read, users:read.email
reminders:write
pins:read, pins:write
```

**User Token Scopes (Optional):**
```
search:read, users.profile:write
reminders:write, channels:read
```

3. Install app to workspace
4. Copy **Bot User OAuth Token** (`xoxb-...`)
5. Copy **Signing Secret** from Basic Information

### 3. Configure Environment

```bash
# Copy template
cp env.example.json env.json

# Edit with your tokens
nano env.json
```

**env.json:**
```json
{
  "ImageRepository": {
    "ImageConfiguration": {
      "RuntimeEnvironmentVariables": {
        "SLACK_BOT_TOKEN": "xoxb-YOUR-BOT-TOKEN-HERE",
        "SLACK_SIGNING_SECRET": "your-signing-secret-here",
        "SLACK_USER_TOKEN": "xoxp-YOUR-USER-TOKEN-HERE",
        "FASTMCP_PORT": "8000",
        "FASTMCP_HOST": "0.0.0.0",
        "LOG_LEVEL": "INFO",
        "ENVIRONMENT": "production"
      }
    }
  }
}
```

### 4. Installation Options

#### 🖥️ **Option A: Local Development**

```bash
# Install dependencies
pip install -e .

# Run server
python run_server.py
```

**Server will be available at:** `http://localhost:8000/mcp`

#### ☁️ **Option B: AWS Cloud Deployment**

**Prerequisites:**
- AWS CLI configured
- Docker installed

```bash
# Configure AWS credentials
aws configure

# Deploy to AWS App Runner
./deploy.sh
```

**Production URL:** `https://YOUR-SERVICE.us-east-1.awsapprunner.com/mcp`

#### 🐳 **Option C: Docker**

```bash
# Build image
docker build -t mcp-slack-server .

# Run container
docker run -p 8000:8000 \
  -e SLACK_BOT_TOKEN="xoxb-..." \
  -e SLACK_SIGNING_SECRET="your-secret" \
  mcp-slack-server
```

#### 🌐 **Option D: Ngrok Tunnel (Team Sharing)**

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from ngrok.com

# Run MCP server with ngrok tunnel
python run_server_with_ngrok.py --ngrok

# With auth token (recommended)
python run_server_with_ngrok.py --ngrok --ngrok-token YOUR_TOKEN
```

**Result:** Public URL like `https://abc123.ngrok.io/mcp`  
**Use case:** Share with team members, remote access, quick demos

See [NGROK_GUIDE.md](NGROK_GUIDE.md) for detailed instructions.

## 🔧 MCP Client Configuration

### **Cursor IDE Integration**

Add to your Cursor MCP settings:

**Local Development:**
```json
{
  "mcp": {
    "slack-mcp-server": {
      "transport": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Ngrok Tunnel (Team Sharing):**
```json
{
  "mcp": {
    "slack-mcp-server-ngrok": {
      "transport": "streamable-http",
      "url": "https://YOUR-NGROK-URL.ngrok.io/mcp/",
      "headers": {
        "Accept": "application/json, text/event-stream"
      }
    }
  }
}
```

**Production Deployment:**
```json
{
  "mcp": {
    "slack-mcp-server": {
      "transport": "streamable-http",
      "url": "https://YOUR-SERVICE.us-east-1.awsapprunner.com/mcp/",
      "headers": {
        "Accept": "application/json, text/event-stream",
        "Cache-Control": "no-cache"
      }
    }
  }
}
```

### **Claude Desktop Integration**

```json
{
  "mcpServers": {
    "slack-automation": {
      "command": "slack-mcp-server",
      "args": ["--port", "8000"]
    }
  }
}
```

## 🛠️ Available Tools

The server provides **29 powerful tools**:

### **📤 Messaging**
- `send_message` - Send messages to channels
- `reply_to_message` - Reply in threads
- `delete_message` - Delete messages
- `schedule_message` - Schedule future messages

### **🔍 Search & Discovery**
- `search_messages` - Search across workspace
- `get_conversation_history` - Get channel history
- `get_thread_replies` - Get thread conversations

### **👥 People & Channels**
- `list_channels` - List workspace channels
- `list_users` - List workspace members
- `get_user_info` - Get detailed user info
- `find_user_by_email` - Find users by email

### **🏗️ Channel Management**
- `create_channel` - Create new channels
- `archive_channel` - Archive channels
- `set_channel_topic` - Set channel topics
- `set_channel_description` - Set descriptions

### **📎 File Operations**
- `upload_file` - Upload files to channels
- `list_files` - List workspace files
- `get_file` - Get file information
- `delete_file` - Delete files

### **🎭 Interactions**
- `add_reaction` - Add emoji reactions
- `pin_message` - Pin important messages
- `unpin_message` - Unpin messages

### **⚙️ Advanced**
- `set_user_status` - Update user status
- `create_reminder` - Set reminders
- `get_team_info` - Get workspace info
- `list_emojis` - List custom emojis

## 🧪 Development

### **Testing**

```bash
# Run all tests
pytest

# With coverage
pytest --cov=slack_mcp_app --cov-report=html

# Run specific test
pytest tests/test_slack_mcp_server.py::TestSlackMCPServer::test_list_channels
```

### **Code Quality**

```bash
# Format code
black .
isort .

# Lint
flake8 .
mypy slack_mcp_app/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### **Security Scanning**

```bash
# Security vulnerabilities
bandit -r slack_mcp_app/

# Dependency security
safety check
```

## 🔒 Security

- ✅ **Token Encryption**: All tokens stored securely
- ✅ **Environment Isolation**: Environment variables only
- ✅ **Rate Limiting**: Built-in request throttling  
- ✅ **CORS Protection**: Configurable origins
- ✅ **Security Scanning**: Automated vulnerability checks

**Security Policy:** [SECURITY.md](SECURITY.md)

## 📊 Monitoring & Logs

### **Health Checks**

```bash
# Local
curl http://localhost:8000/health

# Production  
curl https://YOUR-SERVICE.us-east-1.awsapprunner.com/health
```

### **Logs**

```bash
# View server logs
docker logs mcp-slack-server

# AWS CloudWatch (for App Runner)
aws logs tail /aws/apprunner/mcp-slack-server --follow
```

### **Metrics**

- Request/response times
- Error rates
- Tool usage statistics
- Memory/CPU utilization

## 🔄 CI/CD Pipeline

Automated **GitHub Actions** workflow:

1. **🧪 Testing**: Python 3.11 & 3.12
2. **🎨 Linting**: Black, isort, flake8, mypy
3. **🔒 Security**: Bandit, Safety scanning
4. **🐳 Docker**: Multi-platform builds
5. **🚀 Deployment**: AWS App Runner
6. **📢 Notifications**: Slack alerts

**Pipeline Status:** [![CI/CD](https://github.com/bahakizil/mcp-slack-server/actions/workflows/ci.yml/badge.svg)](https://github.com/bahakizil/mcp-slack-server/actions)

## 🌍 Multi-Team Setup

### **Shared Configuration**

For team members to use the same deployment:

1. **Share the production URL**
2. **Provide MCP configuration JSON**
3. **No local setup required!**

**Team Configuration:**
```json
{
  "mcp": {
    "slack-team-automation": {
      "transport": "streamable-http",
      "url": "https://YOUR-SHARED-SERVICE.us-east-1.awsapprunner.com/mcp/",
      "headers": {
        "Accept": "application/json, text/event-stream"
      }
    }
  }
}
```

### **Environment Separation**

```bash
# Development
ENVIRONMENT=development

# Staging  
ENVIRONMENT=staging

# Production
ENVIRONMENT=production
```

## 📚 Documentation

- **[Installation Guide](INSTALLATION_GUIDE.md)** - Complete step-by-step setup
- **[Quick Start](QUICKSTART.md)** - Get running in 5 minutes
- **[API Reference](docs/api-reference.md)** - Complete tool documentation
- **[Deployment Guide](docs/deployment.md)** - Detailed setup instructions
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues & solutions
- **[Security Policy](SECURITY.md)** - Security guidelines

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** Pull Request

**Development Setup:**
```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/mcp-slack-server.git

# Install development dependencies
pip install -e ".[dev,test]"

# Run pre-commit hooks
pre-commit install
```

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file.

## 🆘 Support

- **🐛 Issues**: [GitHub Issues](https://github.com/bahakizil/mcp-slack-server/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/bahakizil/mcp-slack-server/discussions)
- **📧 Security**: See [SECURITY.md](SECURITY.md)

## 🙏 Acknowledgments

- **[FastMCP](https://github.com/jlowin/fastmcp)** - Excellent MCP framework
- **[Slack SDK](https://github.com/slackapi/python-slack-sdk)** - Official Python SDK
- **[AWS App Runner](https://aws.amazon.com/apprunner/)** - Serverless deployment
- **Community** - Thank you for contributions!

---

**⭐ Star this repository if it helped you automate your Slack workspace!**

**🔗 Share with your team for collaborative automation!** 