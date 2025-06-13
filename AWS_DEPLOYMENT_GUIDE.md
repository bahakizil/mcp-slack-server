# ☁️ AWS Deployment Guide

Complete step-by-step guide for deploying MCP Slack Server to AWS App Runner for production use.

**⏱️ Total Time:** 15-20 minutes  
**🎯 Result:** Production-ready MCP server with public URL  
**💰 Cost:** ~$5-10/month for small usage

---

## 🔧 **Prerequisites**

Before starting, ensure you have:

- ✅ **AWS Account** (free tier eligible)
- ✅ **AWS CLI installed** (version 2.x recommended)
- ✅ **Docker installed** and running
- ✅ **Git repository** with your configured MCP server
- ✅ **env.json** file with your Slack tokens

---

## 🚀 **Step 1: Set Up AWS CLI**

### 1.1 Install AWS CLI (if not installed)

**macOS:**
```bash
# Using Homebrew
brew install awscli

# Or download installer
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

**Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Windows:**
```bash
# Download and run AWS CLI MSI installer
# https://aws.amazon.com/cli/
```

### 1.2 Verify Installation
```bash
aws --version
# Should show: aws-cli/2.x.x
```

### 1.3 Configure AWS Credentials

**Option A: Interactive Configuration**
```bash
aws configure
```

**You'll be prompted for:**
- **AWS Access Key ID:** Your access key
- **AWS Secret Access Key:** Your secret key  
- **Default region:** `us-east-1` (recommended)
- **Default output format:** `json`

**Option B: Using Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### 1.4 Test AWS Connection
```bash
aws sts get-caller-identity
```

**Expected output:**
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

---

## 🐳 **Step 2: Install and Configure Docker**

### 2.1 Install Docker

**macOS:**
- Download Docker Desktop from https://docker.com/products/docker-desktop
- Install and start Docker Desktop

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and log back in
```

**Windows:**
- Download Docker Desktop from https://docker.com/products/docker-desktop
- Install and start Docker Desktop

### 2.2 Verify Docker Installation
```bash
docker --version
docker run hello-world
```

---

## 📋 **Step 3: Prepare Your Project**

### 3.1 Ensure Configuration is Ready
```bash
# Check env.json exists and has tokens
cat env.json

# Should contain your Slack tokens:
# {
#   "ImageRepository": {
#     "ImageConfiguration": {
#       "RuntimeEnvironmentVariables": {
#         "SLACK_BOT_TOKEN": "xoxb-...",
#         "SLACK_SIGNING_SECRET": "...",
#         ...
#       }
#     }
#   }
# }
```

### 3.2 Test Local Server (Optional)
```bash
# Quick local test before deployment
python run_server.py &
curl http://localhost:8000/health
kill %1  # Stop local server
```

---

## 🚀 **Step 4: Automated Deployment**

### 4.1 Run Deployment Script
```bash
./deploy.sh
```

The script will automatically:
- ✅ Check prerequisites (AWS CLI, Docker, credentials)
- ✅ Get AWS account information
- ✅ Create ECR repository if needed
- ✅ Build Docker image for linux/amd64 platform
- ✅ Push image to ECR
- ✅ Create or update App Runner service
- ✅ Display service URL

### 4.2 Monitor Deployment Progress

**Watch the output for:**
```bash
🚀 MCP Slack Server - AWS Deployment
========================================
🔍 Checking prerequisites...
✅ All prerequisites met!
📊 Getting AWS account information...
   Account ID: 123456789012
   Region: us-east-1
🏗️  Ensuring ECR repository exists...
   ✅ ECR repository already exists
📦 Building Docker image...
[+] Building 45.2s (15/15) FINISHED
🏷️  Tagging image...
🔐 Logging into ECR...
Login Succeeded
⬆️  Pushing to ECR...
✅ Docker image pushed successfully!
🎯 Deploying to App Runner...
   Creating new App Runner service...
   ⏳ Service creation initiated...
   ℹ️  This may take 5-10 minutes for first deployment
```

---

## 🌐 **Step 5: Get Your Production URL**

### 5.1 Wait for Service Creation
The deployment script will show:
```bash
🌐 Getting service URL...
   📍 Service URL: https://abc123def456.us-east-1.awsapprunner.com
   🔧 MCP Endpoint: https://abc123def456.us-east-1.awsapprunner.com/mcp
   💾 URL saved to .deployment-url
```

### 5.2 Verify Deployment
```bash
# Test health endpoint
curl https://YOUR-SERVICE-URL.us-east-1.awsapprunner.com/health

# Test MCP endpoint
curl -H "Accept: application/json, text/event-stream" \
     https://YOUR-SERVICE-URL.us-east-1.awsapprunner.com/mcp
```

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "id": "server-error",
  "error": {
    "code": -32600,
    "message": "Bad Request: Missing session ID"
  }
}
```
*(This error is normal - it means the server is running)*

---

## 🔧 **Step 6: Configure MCP Client for Production**

### 6.1 Update Cursor Configuration

**Edit `~/.cursor/mcp.json`:**
```json
{
  "mcp": {
    "slack-mcp-server-production": {
      "transport": "streamable-http",
      "url": "https://YOUR-SERVICE-URL.us-east-1.awsapprunner.com/mcp/",
      "headers": {
        "Accept": "application/json, text/event-stream",
        "Cache-Control": "no-cache"
      }
    }
  }
}
```

### 6.2 Test Production Connection

1. **Restart Cursor completely**
2. **Go to Tools tab**
3. **Enable `slack-mcp-server-production`**
4. **Verify 25 tools are available**

### 6.3 Test Production Functionality
**Try in Cursor:**
> "Using production server, list my Slack channels"

---

## 📊 **Step 7: Monitor and Manage**

### 7.1 View Service in AWS Console

1. Go to **AWS Console → App Runner**
2. Find your service: `slack-mcp-server`
3. Check **Service status**, **Logs**, **Metrics**

### 7.2 View Application Logs
```bash
# Using AWS CLI
aws logs tail /aws/apprunner/slack-mcp-server --follow

# Or in AWS Console: CloudWatch → Log groups
```

### 7.3 Service Management Commands

**Check service status:**
```bash
aws apprunner describe-service \
  --service-arn $(aws apprunner list-services \
  --query "ServiceSummaryList[?ServiceName=='slack-mcp-server'].ServiceArn" \
  --output text)
```

**Trigger new deployment:**
```bash
aws apprunner start-deployment \
  --service-arn $(aws apprunner list-services \
  --query "ServiceSummaryList[?ServiceName=='slack-mcp-server'].ServiceArn" \
  --output text)
```

**Pause service (to save costs):**
```bash
aws apprunner pause-service \
  --service-arn $(aws apprunner list-services \
  --query "ServiceSummaryList[?ServiceName=='slack-mcp-server'].ServiceArn" \
  --output text)
```

**Resume service:**
```bash
aws apprunner resume-service \
  --service-arn $(aws apprunner list-services \
  --query "ServiceSummaryList[?ServiceName=='slack-mcp-server'].ServiceArn" \
  --output text)
```

---

## 🔄 **Step 8: Update Deployments**

### 8.1 Code Changes
When you make changes to your code:

```bash
# 1. Commit changes
git add .
git commit -m "feat: add new feature"

# 2. Re-deploy
./deploy.sh
```

### 8.2 Environment Variable Updates

**To update Slack tokens or other environment variables:**

1. **Update `env.json`** with new values
2. **Re-run deployment:**
   ```bash
   ./deploy.sh
   ```

### 8.3 Manual AWS Console Updates

1. **AWS Console → App Runner → slack-mcp-server**
2. **Configuration → Edit**
3. **Environment variables → Update values**
4. **Deploy**

---

## 💰 **Step 9: Cost Management**

### 9.1 App Runner Pricing

**Current pricing (us-east-1):**
- **vCPU:** $0.064 per vCPU per hour
- **Memory:** $0.007 per GB per hour
- **Request:** $0.0000008 per request

**Default configuration (0.25 vCPU, 0.5 GB):**
- **Base cost:** ~$5.50/month if running 24/7
- **Request cost:** Minimal for typical usage

### 9.2 Cost Optimization

**Auto-pause when idle:**
```bash
# Pause during off-hours
aws apprunner pause-service --service-arn YOUR-SERVICE-ARN

# Resume when needed
aws apprunner resume-service --service-arn YOUR-SERVICE-ARN
```

**Or use Lambda scheduling:**
- Create Lambda functions to pause/resume on schedule
- Use CloudWatch Events to trigger

### 9.3 Monitor Costs

1. **AWS Console → Billing & Cost Management**
2. **Cost Explorer → App Runner costs**
3. **Set up billing alerts**

---

## 🐛 **Troubleshooting**

### ❌ **"AWS CLI not found"**
```bash
# Install AWS CLI (see Step 1.1)
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

### ❌ **"Unable to locate credentials"**
```bash
# Configure credentials
aws configure

# Or check existing config
aws configure list
cat ~/.aws/credentials
```

### ❌ **"Docker daemon not running"**
```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker service (Linux)
sudo systemctl start docker
```

### ❌ **"ECR repository does not exist"**
```bash
# Create repository manually
aws ecr create-repository --repository-name slack-mcp-server --region us-east-1
```

### ❌ **"Service creation failed"**

**Check IAM permissions:**
```bash
# Your AWS user needs these permissions:
# - apprunner:*
# - ecr:*
# - iam:CreateRole
# - iam:AttachRolePolicy
```

**Check resource limits:**
- AWS account may have App Runner service limits
- Contact AWS support if needed

### ❌ **"Build failed for platform linux/amd64"**
```bash
# On Apple Silicon Macs, ensure Docker can build x86 images
docker buildx create --use
docker buildx build --platform linux/amd64 -t test .
```

### ❌ **"Service URL not available"**
```bash
# Wait 5-10 minutes for first deployment
# Check service status
aws apprunner describe-service --service-arn YOUR-SERVICE-ARN
```

---

## 🌍 **Step 10: Team Sharing**

### 10.1 Share Production URL

**Send team members:**
1. **Production URL:** `https://YOUR-SERVICE.us-east-1.awsapprunner.com/mcp/`
2. **Cursor configuration:**
   ```json
   {
     "mcp": {
       "slack-team-automation": {
         "transport": "streamable-http",
         "url": "https://YOUR-SERVICE.us-east-1.awsapprunner.com/mcp/",
         "headers": {
           "Accept": "application/json, text/event-stream"
         }
       }
     }
   }
   ```

### 10.2 No Additional Setup Required

Team members only need:
- ✅ **Cursor IDE** with MCP configuration
- ✅ **Production URL** (no local setup needed)
- ✅ **Access to same Slack workspace**

---

## 🎯 **Success Checklist**

After completing this guide, you should have:

- ✅ **AWS CLI** configured and tested
- ✅ **Docker** installed and running
- ✅ **ECR repository** created for your images
- ✅ **App Runner service** running and healthy
- ✅ **Production URL** accessible and responding
- ✅ **Cursor IDE** connected to production server
- ✅ **25 Slack tools** working in production
- ✅ **Team members** able to connect

---

## 📚 **Additional Resources**

### AWS Documentation
- **[App Runner User Guide](https://docs.aws.amazon.com/apprunner/)**
- **[ECR User Guide](https://docs.aws.amazon.com/ecr/)**
- **[AWS CLI Reference](https://docs.aws.amazon.com/cli/)**

### Related Guides
- **[Installation Guide](INSTALLATION_GUIDE.md)** - Local setup
- **[Quick Start](QUICKSTART.md)** - Fast local development
- **[README](README.md)** - Complete project documentation

---

## 🆘 **Get Help**

- 🐛 **Issues:** [GitHub Issues](https://github.com/bahakizil/mcp-slack-server/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/bahakizil/mcp-slack-server/discussions)
- 📧 **AWS Support:** AWS Console → Support Center

---

**🎉 Congratulations! Your MCP Slack Server is now running in production with enterprise-grade reliability!** 