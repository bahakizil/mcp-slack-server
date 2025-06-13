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
    print("\n📝 Setting up environment configuration...")
    
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
    
    print(f"✅ Configuration saved to {env_file}")


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
        show_usage_instructions()
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 