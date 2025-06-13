# 📋 Step-by-Step Installation Guide

Complete guide for setting up MCP Slack Server in your own workspace and connecting it to Cursor IDE.

**⏱️ Total Time:** 10-15 minutes  
**🎯 Result:** 25 powerful Slack automation tools in Cursor

---

## 🚀 **Step 1: Download Repository**

```bash
git clone https://github.com/bahakizil/mcp-slack-server.git
cd mcp-slack-server
```

---

## 🔑 **Step 2: Create Slack App (5 minutes)**

### 2.1 Create New App
1. Go to **Slack API Console:** https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. **App Name:** `MCP Slack Server`
4. **Workspace:** Select your Slack workspace
5. Click **"Create App"**

### 2.2 Configure Bot Permissions
**Navigate to "OAuth & Permissions" → "Bot Token Scopes"**

**Add these scopes:**
```
channels:read
channels:write  
channels:history
chat:write
chat:write.public
files:read
files:write
reactions:read
reactions:write
users:read
users:read.email
reminders:write
pins:read
pins:write
```

### 2.3 Install to Workspace
1. Click **"Install to Workspace"** button
2. Click **"Allow"** to grant permissions
3. **Copy the Bot User OAuth Token** (starts with `xoxb-`)

### 2.4 Get Signing Secret
1. Go to **"Basic Information"** in left menu
2. Under **"App Credentials" → "Signing Secret"** → Click **"Show"**
3. **Copy the signing secret**

---

## ⚡ **Step 3: Automated Setup (Recommended)**

Run the interactive setup script:

```bash
python setup.py
```

**The script will ask for:**
- 🤖 **Slack Bot Token:** Paste your `xoxb-...` token
- 🔒 **Slack Signing Secret:** Paste your signing secret  
- 👤 **Slack User Token:** (optional, press Enter to skip)

**The script will automatically:**
- ✅ Install all Python dependencies
- ✅ Create configuration file with your tokens
- ✅ Run tests to verify everything works
- ✅ Show you next steps

---

## 🖥️ **Step 4: Start the Server**

```bash
python run_server.py
```

**Your server will be running at:** `http://localhost:8000/mcp`

**Keep this terminal open** - the server needs to run for MCP tools to work.

---

## 🔧 **Step 5: Connect to Cursor IDE**

### 5.1 Open Cursor MCP Settings
**Edit or create:** `~/.cursor/mcp.json`

### 5.2 Add Configuration
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

### 5.3 Restart Cursor
1. **Close Cursor completely**
2. **Reopen Cursor**
3. Go to **Tools tab**
4. **Enable `slack-mcp-server`**

---

## ✅ **Step 6: Test Your Setup**

### 6.1 Verify Tools Available
You should see **25 Slack tools** in Cursor:
- `send_message` - Send messages to channels
- `list_channels` - List workspace channels
- `add_reaction` - Add emoji reactions
- `upload_file` - Upload files to channels
- `create_channel` - Create new channels
- ...and 24 more!

### 6.2 Test Basic Functionality
**Try this in Cursor:**
> "List my Slack channels"

**Or:**
> "Send a test message to #general channel"

---

## 🛠️ **Available Tools Reference**

Once connected, you can use these tools via Cursor:

### 📧 **Messaging**
- `send_message` - Send messages to channels
- `reply_to_message` - Reply in threads  
- `delete_message` - Delete messages
- `schedule_message` - Schedule future messages
- `search_messages` - Search across workspace

### 👥 **People & Channels**  
- `list_channels` - List workspace channels
- `list_users` - List team members
- `get_user_info` - Get detailed user info
- `find_user_by_email` - Find users by email
- `create_channel` - Create new channels
- `archive_channel` - Archive channels
- `set_channel_topic` - Set channel topics

### 📎 **Files & Interactions**
- `upload_file` - Upload files to channels
- `list_files` - List workspace files
- `delete_file` - Delete files
- `add_reaction` - React with emojis
- `pin_message` - Pin important messages
- `unpin_message` - Unpin messages

### ⚙️ **Advanced Features**
- `get_conversation_history` - Get channel history
- `get_thread_replies` - Get thread conversations
- `set_user_status` - Update user status
- `create_reminder` - Set reminders
- `get_team_info` - Get workspace info
- `list_emojis` - List custom emojis

---

## 🐛 **Troubleshooting**

### ❌ **"Module not found" error:**
```bash
pip install -e .
```

### ❌ **Cursor shows red tools:**
**Check server is running:**
```bash
curl http://localhost:8000/mcp
```

**Verify MCP configuration:**
```bash
cat ~/.cursor/mcp.json
```

**Restart Cursor completely**

### ❌ **"Slack API Error":**
- ✅ Bot token starts with `xoxb-`?
- ✅ Bot installed to workspace?
- ✅ Bot has required permissions?
- ✅ Bot invited to channels you want to use?

### ❌ **Bot can't see channels:**
**Invite bot to channels in Slack:**
```
/invite @mcp-slack-server
```

### ❌ **Server won't start:**
**Check Python version:**
```bash
python --version  # Should be 3.11+
```

**Check port availability:**
```bash
lsof -i :8000  # Should be empty
```

---

## 🚀 **Alternative: Manual Setup**

If automated setup doesn't work:

### Manual Installation
```bash
# 1. Install dependencies
pip install -e .

# 2. Create configuration
cp env.example.json env.json
# Edit env.json with your tokens

# 3. Run server
python run_server.py
```

### Manual Configuration (env.json)
```json
{
  "ImageRepository": {
    "ImageConfiguration": {
      "RuntimeEnvironmentVariables": {
        "SLACK_BOT_TOKEN": "xoxb-YOUR-BOT-TOKEN-HERE",
        "SLACK_SIGNING_SECRET": "your-signing-secret-here",
        "FASTMCP_PORT": "8000",
        "FASTMCP_HOST": "0.0.0.0",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

---

## ☁️ **Production Deployment (Optional)**

### Deploy to AWS
```bash
# Prerequisites: AWS CLI configured, Docker installed
aws configure

# Deploy with one command
./deploy.sh
```

### Production Cursor Configuration
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

---

## 🎯 **Success Checklist**

After following this guide, you should have:

- ✅ **Slack App** created and configured
- ✅ **Bot tokens** obtained and configured
- ✅ **MCP Server** running locally
- ✅ **Cursor IDE** connected and showing 25 tools
- ✅ **Test message** sent successfully

---

## 📚 **Next Steps**

1. **Explore automation possibilities** with 25 tools
2. **Create custom workflows** using Cursor + Slack
3. **Share with your team** for collaborative automation
4. **Deploy to production** for always-on availability

---

## 🆘 **Get Help**

- 📚 **Full Documentation:** [README.md](README.md)
- ⚡ **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- 🐛 **Report Issues:** [GitHub Issues](https://github.com/bahakizil/mcp-slack-server/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/bahakizil/mcp-slack-server/discussions)

---

**🎉 Congratulations! You now have a powerful Slack automation system running with 25 tools at your disposal!** 