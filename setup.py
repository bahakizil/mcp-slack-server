#!/usr/bin/env python3
"""
MCP Slack Server Setup Script
Automates the installation and configuration process
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run shell command safely."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        sys.exit(1)
    return result


def create_env_config():
    """Create environment configuration from template."""
    print("\n📝 Setting up Slack environment configuration...")
    
    env_example = Path("env.example.json")
    env_file = Path("env.json")
    
    if not env_example.exists():
        print("❌ env.example.json not found!")
        sys.exit(1)
    
    if env_file.exists():
        print("⚠️  env.json already exists, backing up...")
        env_file.rename(f"env.json.backup")
    
    # Load template
    with open(env_example) as f:
        config = json.load(f)
    
    env_vars = config["ImageRepository"]["ImageConfiguration"]["RuntimeEnvironmentVariables"]
    
    print("\n🔑 Please provide your Slack credentials:")
    print("   Get these from: https://api.slack.com/apps")
    
    # Get user input
    bot_token = input("\n🤖 Slack Bot Token (xoxb-...): ").strip()
    if not bot_token.startswith("xoxb-"):
        print("❌ Bot token should start with 'xoxb-'")
        sys.exit(1)
    
    signing_secret = input("🔒 Slack Signing Secret: ").strip()
    
    user_token = input("👤 Slack User Token (xoxp-..., optional): ").strip()
    if user_token and not user_token.startswith("xoxp-"):
        print("❌ User token should start with 'xoxp-'")
        sys.exit(1)
    
    # Update configuration
    env_vars["SLACK_BOT_TOKEN"] = bot_token
    env_vars["SLACK_SIGNING_SECRET"] = signing_secret
    if user_token:
        env_vars["SLACK_USER_TOKEN"] = user_token
    
    # Save configuration
    with open(env_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Slack configuration saved to {env_file}")


def create_aws_config():
    """Create AWS configuration from template."""
    print("\n☁️  Setting up AWS deployment configuration...")
    
    aws_example = Path("aws.example.json")
    aws_file = Path("aws.json")
    
    if not aws_example.exists():
        print("❌ aws.example.json not found!")
        sys.exit(1)
    
    # Check if user wants AWS setup
    setup_aws = input("\n🤔 Do you want to setup AWS deployment? (y/N): ").strip().lower()
    if setup_aws not in ['y', 'yes']:
        print("⏭️  Skipping AWS configuration (you can setup later)")
        return
    
    if aws_file.exists():
        print("⚠️  aws.json already exists, backing up...")
        aws_file.rename(f"aws.json.backup")
    
    # Load template
    with open(aws_example) as f:
        config = json.load(f)
    
    print("\n🔑 Please provide your AWS credentials:")
    print("   Get these from: https://console.aws.amazon.com/iam/")
    print("   📚 Guide: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html")
    
    # Get AWS credentials
    account_id = input("\n🏢 AWS Account ID (12-digit number): ").strip()
    if not account_id.isdigit() or len(account_id) != 12:
        print("❌ AWS Account ID should be a 12-digit number")
        sys.exit(1)
    
    access_key = input("🔑 AWS Access Key ID (AKIA...): ").strip()
    if not access_key.startswith("AKIA"):
        print("❌ AWS Access Key ID should start with 'AKIA'")
        sys.exit(1)
    
    secret_key = input("🔒 AWS Secret Access Key: ").strip()
    
    region = input("🌍 AWS Default Region (us-east-1): ").strip() or "us-east-1"
    
    # Optional: ARN for more advanced configurations
    user_arn = input("👤 AWS User ARN (optional): ").strip()
    
    # Service configuration
    service_name = input("🚀 App Runner Service Name (slack-mcp-server): ").strip() or "slack-mcp-server"
    ecr_repo = input("📦 ECR Repository Name (slack-mcp-server): ").strip() or "slack-mcp-server"
    
    # Update configuration
    config["aws_account_id"] = account_id
    config["aws_access_key_id"] = access_key
    config["aws_secret_access_key"] = secret_key
    config["aws_default_region"] = region
    config["service_name"] = service_name
    config["ecr_repository"] = ecr_repo
    
    if user_arn:
        config["aws_user_arn"] = user_arn
    
    # Save configuration
    with open(aws_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ AWS configuration saved to {aws_file}")
    print("🔧 AWS CLI will be automatically configured for deployment")


def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        sys.exit(1)
    
    # Install package in production mode
    run_command("pip install -e .")
    print("✅ Dependencies installed successfully")





def show_usage_instructions():
    """Show post-installation usage instructions."""
    print("\n🎉 Installation completed successfully!")
    print("\n" + "="*60)
    print("🚀 USAGE INSTRUCTIONS")
    print("="*60)
    
    print("\n📍 LOCAL DEVELOPMENT:")
    print("   python run_server.py")
    print("   # Server: http://localhost:8000/mcp")
    

    
    print("\n📍 DOCKER:")
    print("   docker build -t mcp-slack-server .")
    print("   docker run -p 8000:8000 mcp-slack-server")
    
    print("\n📍 AWS DEPLOYMENT:")
    print("   ./deploy.sh")
    
    print("\n📍 MCP CLIENT CONFIGURATION (Cursor):")
    print('   Add to ~/.cursor/mcp.json:')
    print('   {')
    print('     "mcp": {')
    print('       "slack-mcp-server": {')
    print('         "transport": "http",')
    print('         "url": "http://localhost:8000/mcp"')
    print('       }')
    print('     }')
    print('   }')
    
    print("\n🛠️  AVAILABLE TOOLS: 29 Slack automation tools")
    print("📚 Documentation: README.md")
    print("🐛 Issues: https://github.com/bahakizil/mcp-slack-server/issues")


def main():
    """Main setup function."""
    print("🚀 MCP Slack Server Setup")
    print("="*40)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    try:
        # Setup steps
        install_dependencies()
        create_env_config()
        create_aws_config()
        show_usage_instructions()
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 