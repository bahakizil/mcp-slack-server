# ⚡ Quick Start Guide

Get your MCP Slack Server running in **5 minutes**!

## 🚀 Option 1: One-Command Setup (Recommended)

```bash
git clone https://github.com/bahakizil/mcp-slack-server.git
cd mcp-slack-server
python setup.py
```

The setup script will:
- ✅ Install all dependencies
- ✅ Guide you through Slack configuration  
- ✅ Run tests to verify everything works
- ✅ Show you exactly how to run the server

## 🔑 Before You Start

### Get Your Slack Tokens (2 minutes)

1. Go to [Slack API Console](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. App name: `MCP Slack Server`, choose your workspace
4. Go to **"OAuth & Permissions"**
5. Add these **Bot Token Scopes**:
   ```
   channels:read, channels:write, channels:history
   chat:write, chat:write.public  
   files:read, files:write
   reactions:read, reactions:write
   users:read, users:read.email
   reminders:write, pins:read, pins:write
   ```
6. Click **"Install to Workspace"**
7. Copy your **Bot User OAuth Token** (`xoxb-...`)
8. Go to **"Basic Information"** → Copy **Signing Secret**

## 🖥️ Option 2: Manual Local Setup

```bash
# 1. Clone repository
git clone https://github.com/bahakizil/mcp-slack-server.git
cd mcp-slack-server

# 2. Install dependencies  
pip install -e ".[dev,test]"

# 3. Configure environment
cp env.example.json env.json
# Edit env.json with your Slack tokens

# 4. Run server
python run_server.py
```

**Your server:** `http://localhost:8000/mcp`

## ☁️ Option 3: Deploy to AWS (Production)

```bash
# Prerequisites: AWS CLI configured, Docker installed
aws configure  # Set your AWS credentials

# Deploy with one command
./deploy.sh
```

**Your production URL:** `https://YOUR-SERVICE.us-east-1.awsapprunner.com/mcp`

## 🔧 Connect to Cursor

### Local Development
Add to `~/.cursor/mcp.json`:
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

### Production
```json
{
  "mcp": {
    "slack-mcp-server": {
      "transport": "streamable-http", 
      "url": "https://YOUR-SERVICE.us-east-1.awsapprunner.com/mcp/",
      "headers": {
        "Accept": "application/json, text/event-stream"
      }
    }
  }
}
```

## ✅ Test Your Setup

1. **Restart Cursor** completely
2. Go to **Tools** tab → Enable `slack-mcp-server`
3. You should see **29 Slack tools** available! 🎉

## 🛠️ Available Tools

Once connected, you can use these tools via any MCP client:

### 📧 **Messaging**
- `send_message` - Send messages to channels
- `reply_to_message` - Reply in threads  
- `search_messages` - Search across workspace

### 👥 **People & Channels**  
- `list_channels` - List workspace channels
- `list_users` - List team members
- `create_channel` - Create new channels

### 📎 **Files & Reactions**
- `upload_file` - Upload files to channels
- `add_reaction` - React with emojis
- `pin_message` - Pin important messages

**...and 20+ more tools!** See [README.md](README.md) for complete list.

## 🐛 Troubleshooting

### Common Issues

**❌ "Module not found" error:**
```bash
pip install -e ".[dev,test]"
```

**❌ Cursor shows red tools:**
- Check your MCP configuration JSON syntax
- Restart Cursor completely
- Verify server is running: `curl http://localhost:8000/mcp`

**❌ "Slack API Error":**
- Verify your bot token starts with `xoxb-`
- Check bot has required permissions in Slack workspace
- Ensure bot is added to channels you want to use

**❌ AWS deployment fails:**
- Run `aws configure` to set credentials
- Ensure Docker is running
- Check you have ECR permissions

### Get Help

- 📚 **Full docs:** [README.md](README.md)
- 🐛 **Report issues:** [GitHub Issues](https://github.com/bahakizil/mcp-slack-server/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/bahakizil/mcp-slack-server/discussions)

## 🎯 What's Next?

Once your server is running:

1. **Test basic functionality:** Try sending a message to your Slack
2. **Explore automation:** Use the 29 tools for workflow automation  
3. **Deploy for team:** Share your production URL with teammates
4. **Customize:** Fork the repo and add your own tools

---

**⚡ Most users get this working in under 5 minutes!**

**🔗 Share this guide with your team for instant Slack automation!** 