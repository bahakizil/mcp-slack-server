#!/usr/bin/env python3
"""
MCP Slack Server with Ngrok Tunnel Support
Runs the existing MCP server and optionally creates an ngrok tunnel
"""

import json
import os
import subprocess
import sys
import time
import threading
from pathlib import Path
import argparse

BASE_DIR = Path(__file__).resolve().parent
ENV_JSON = BASE_DIR / "env.json"

class NgrokTunnel:
    """Ngrok tunnel management for MCP server"""
    
    def __init__(self, port=8000, auth_token=None):
        self.port = port
        self.auth_token = auth_token
        self.tunnel_url = None
        self.process = None
        
    def check_ngrok_installed(self):
        """Check if ngrok is installed"""
        try:
            result = subprocess.run(['ngrok', 'version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def install_instructions(self):
        """Show ngrok installation instructions"""
        print("\n🚨 Ngrok bulunamadı! Yüklemek için:")
        print("\n📦 Kurulum:")
        print("  # macOS")
        print("  brew install ngrok")
        print("\n  # Linux")
        print("  curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null")
        print("  echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list")
        print("  sudo apt update && sudo apt install ngrok")
        print("\n  # Windows")
        print("  choco install ngrok")
        print("\n🔑 Auth token ayarlamak için:")
        print("  ngrok config add-authtoken YOUR_TOKEN")
        print("  # Token almak için: https://dashboard.ngrok.com/get-started/your-authtoken")
        
    def setup_auth(self):
        """Setup ngrok auth token if provided"""
        if self.auth_token:
            try:
                subprocess.run(['ngrok', 'config', 'add-authtoken', self.auth_token], 
                             check=True, capture_output=True)
                print(f"✅ Ngrok auth token ayarlandı")
            except subprocess.CalledProcessError:
                print(f"❌ Auth token ayarlanamadı: {self.auth_token}")
                
    def start_tunnel(self):
        """Start ngrok tunnel"""
        if not self.check_ngrok_installed():
            self.install_instructions()
            return False
            
        self.setup_auth()
        
        print(f"🌐 Ngrok tunnel başlatılıyor (port: {self.port})...")
        
        try:
            # Start ngrok tunnel
            cmd = ['ngrok', 'http', str(self.port), '--log=stdout']
            self.process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for tunnel URL
            for i in range(30):  # 30 second timeout
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    print(f"❌ Ngrok başlatılamadı:")
                    print(f"STDOUT: {stdout}")
                    print(f"STDERR: {stderr}")
                    return False
                    
                try:
                    # Get tunnel info from ngrok API
                    import requests
                    response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
                    tunnels = response.json()
                    
                    if tunnels.get('tunnels'):
                        self.tunnel_url = tunnels['tunnels'][0]['public_url']
                        break
                except:
                    pass
                    
                time.sleep(1)
                
            if self.tunnel_url:
                print(f"✅ Ngrok tunnel aktif!")
                print(f"📍 Public URL: {self.tunnel_url}")
                print(f"🔧 MCP Endpoint: {self.tunnel_url}/mcp")
                print(f"📊 Dashboard: http://localhost:4040")
                return True
            else:
                print("❌ Tunnel URL alınamadı")
                return False
                
        except Exception as e:
            print(f"❌ Ngrok tunnel hatası: {e}")
            return False
            
    def stop_tunnel(self):
        """Stop ngrok tunnel"""
        if self.process:
            print("🛑 Ngrok tunnel durduruluyor...")
            self.process.terminate()
            self.process.wait()
            self.process = None
            print("✅ Tunnel durduruldu")
            
    def get_mcp_config(self):
        """Get MCP client configuration for ngrok tunnel"""
        if not self.tunnel_url:
            return None
            
        return {
            "mcp": {
                "slack-mcp-server-ngrok": {
                    "transport": "streamable-http",
                    "url": f"{self.tunnel_url}/mcp/",
                    "headers": {
                        "Accept": "application/json, text/event-stream",
                        "Cache-Control": "no-cache"
                    }
                }
            }
        }

def start_mcp_server():
    """Start the MCP server (existing logic)"""
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

    # Set port from environment variable
    port = os.getenv("PORT", "8000")
    os.environ["FASTMCP_PORT"] = port
    os.environ["FASTMCP_HOST"] = "0.0.0.0"

    print("[MCP Server] Environment variables loaded")
    print(f"[MCP Server] Port: {port}")

    # Import and run the server
    try:
        from slack_mcp_app.slack_mcp_server import mcp
        
        # Run in a separate thread to allow ngrok control
        def run_server():
            mcp.run(transport="streamable-http", host="0.0.0.0", port=int(port))
            
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        return int(port), server_thread
        
    except Exception as e:
        print(f"[MCP Server] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='MCP Slack Server with Ngrok Tunnel')
    parser.add_argument('--ngrok', action='store_true', help='Enable ngrok tunnel')
    parser.add_argument('--ngrok-token', help='Ngrok auth token')
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    
    args = parser.parse_args()
    
    print("🚀 MCP Slack Server + Ngrok")
    print("=" * 50)
    
    # Start MCP server
    port, server_thread = start_mcp_server()
    
    # Wait for server to start
    time.sleep(3)
    print(f"✅ MCP Server çalışıyor: http://localhost:{port}/mcp")
    
    ngrok_tunnel = None
    
    if args.ngrok:
        # Start ngrok tunnel
        ngrok_tunnel = NgrokTunnel(port=port, auth_token=args.ngrok_token)
        if ngrok_tunnel.start_tunnel():
            print("\n🔧 MCP Client Konfigürasyonu (Cursor):")
            config = ngrok_tunnel.get_mcp_config()
            print(json.dumps(config, indent=2))
            
            print("\n📋 Kullanım:")
            print("1. Yukarıdaki config'i ~/.cursor/mcp.json dosyasına ekleyin")
            print("2. Cursor'u yeniden başlatın")
            print("3. Tools tab'de 'slack-mcp-server-ngrok' aktif edin")
            print("4. 25 Slack tool'u kullanmaya başlayın!")
        else:
            print("❌ Ngrok tunnel başlatılamadı, sadece local erişim")
    
    print(f"\n🌍 Erişim Seçenekleri:")
    print(f"   Local:  http://localhost:{port}/mcp")
    if ngrok_tunnel and ngrok_tunnel.tunnel_url:
        print(f"   Public: {ngrok_tunnel.tunnel_url}/mcp")
    
    try:
        print("\n💡 CTRL+C ile durdurmak için...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Server durduruluyor...")
        if ngrok_tunnel:
            ngrok_tunnel.stop_tunnel()
        print("✅ Temizlik tamamlandı")

if __name__ == "__main__":
    main() 