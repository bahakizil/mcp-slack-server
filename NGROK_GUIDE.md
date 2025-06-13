# 🌐 Ngrok Tunnel Kullanım Kılavuzu

MCP Slack Server'ınızı ngrok tunnel ile internete açma rehberi.

---

## 🎯 **Ngrok Nedir ve Ne Zaman Kullanılır?**

### **Ngrok Nedir:**
**Ngrok**, yerel geliştirme ortamınızdaki uygulamaları geçici olarak internete açan bir tunnel servisidir.

```
Yerel Server (localhost:8000) → Ngrok → Public URL (https://abc123.ngrok.io)
```

### **Ne Zaman Kullanılır:**

1. **🚀 Hızlı Paylaşım**
   - Takım arkadaşlarınızla MCP server'ınızı paylaşmak
   - Uzaktan çalışırken erişim sağlamak

2. **🧪 Test ve Debug**
   - Farklı ağlardan MCP server'ınızı test etmek
   - Webhook'lar için public endpoint gerektiğinde

3. **📋 Demo ve Sunum**
   - MCP server özelliklerini göstermek
   - Geçici erişim sağlamak

### **Avantajları:**
- ✅ **Hızlı setup** (5 dakika)
- ✅ **Ücretsiz kullanım** (limitli)
- ✅ **HTTPS otomatik**
- ✅ **Gerçek zamanlı monitoring**

### **Dezavantajları:**
- ❌ Ücretsiz sürümde URL her seferinde değişir
- ❌ Güvenlik riski (internet erişimi)
- ❌ Performans overhead
- ❌ Bağlantı limitleri

---

## 🛠️ **Kurulum ve Hazırlık**

### **1. Ngrok Kurulumu**

**macOS:**
```bash
brew install ngrok
```

**Linux:**
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

**Windows:**
```bash
choco install ngrok
```

### **2. Ngrok Hesap Açma**
1. [ngrok.com](https://ngrok.com) adresine gidin
2. Ücretsiz hesap oluşturun
3. Dashboard'dan Auth Token'ınızı alın

### **3. Auth Token Ayarlama**
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

---

## 🚀 **MCP Server + Ngrok Kullanımı**

### **Method 1: Otomatik Script**

```bash
# Ngrok ile birlikte başlat
python run_server_with_ngrok.py --ngrok

# Token ile birlikte başlat
python run_server_with_ngrok.py --ngrok --ngrok-token YOUR_TOKEN
```

**Çıktı:**
```
🚀 MCP Slack Server + Ngrok
==================================================
[MCP Server] Environment variables loaded
[MCP Server] Port: 8000
✅ MCP Server çalışıyor: http://localhost:8000/mcp
🌐 Ngrok tunnel başlatılıyor (port: 8000)...
✅ Ngrok tunnel aktif!
📍 Public URL: https://abc123def456.ngrok.io
🔧 MCP Endpoint: https://abc123def456.ngrok.io/mcp
📊 Dashboard: http://localhost:4040

🔧 MCP Client Konfigürasyonu (Cursor):
{
  "mcp": {
    "slack-mcp-server-ngrok": {
      "transport": "streamable-http",
      "url": "https://abc123def456.ngrok.io/mcp/",
      "headers": {
        "Accept": "application/json, text/event-stream",
        "Cache-Control": "no-cache"
      }
    }
  }
}
```

### **Method 2: Manuel Başlatma**

**Terminal 1 - MCP Server:**
```bash
python run_server.py
```

**Terminal 2 - Ngrok Tunnel:**
```bash
ngrok http 8000
```

---

## 🔧 **Cursor IDE Konfigürasyonu**

### **1. Config Dosyası Düzenleme**
```bash
# Cursor MCP ayar dosyasını açın
nano ~/.cursor/mcp.json
```

### **2. Ngrok Konfigürasyonu Ekleme**
```json
{
  "mcp": {
    "slack-mcp-server-local": {
      "transport": "http",
      "url": "http://localhost:8000/mcp"
    },
    "slack-mcp-server-ngrok": {
      "transport": "streamable-http",
      "url": "https://YOUR-NGROK-URL.ngrok.io/mcp/",
      "headers": {
        "Accept": "application/json, text/event-stream",
        "Cache-Control": "no-cache"
      }
    }
  }
}
```

### **3. Cursor'u Yeniden Başlatma**
1. Cursor'u tamamen kapatın
2. Yeniden açın
3. Tools tab'de `slack-mcp-server-ngrok`'u aktif edin

---

## 🌍 **Paylaşım ve Takım Kullanımı**

### **Takım Arkadaşlarınızla Paylaşım:**

1. **Public URL paylaşın:**
   ```
   MCP Endpoint: https://abc123def456.ngrok.io/mcp
   ```

2. **Cursor konfigürasyonu gönderin:**
   ```json
   {
     "mcp": {
       "shared-slack-server": {
         "transport": "streamable-http",
         "url": "https://abc123def456.ngrok.io/mcp/",
         "headers": {
           "Accept": "application/json, text/event-stream"
         }
       }
     }
   }
   ```

3. **Güvenlik notları:**
   - URL'yi sadece güvendiğiniz kişilerle paylaşın
   - Hassas Slack token'larınızı kontrol edin
   - Kullanım sonrası tunnel'ı kapatmayı unutmayın

---

## 📊 **Monitoring ve Debug**

### **Ngrok Dashboard:**
- **URL:** http://localhost:4040
- **Özellikler:**
  - Gelen request'leri görme
  - Response'ları inceleme
  - Trafik istatistikleri
  - Request replay

### **MCP Server Logları:**
```bash
# Server loglarını takip etme
tail -f /var/log/mcp-server.log

# veya console output'u izleme
python run_server_with_ngrok.py --ngrok --verbose
```

### **Test Komutları:**
```bash
# Health check
curl https://YOUR-NGROK-URL.ngrok.io/health

# MCP endpoint test
curl -H "Accept: application/json" \
     https://YOUR-NGROK-URL.ngrok.io/mcp

# Slack tools test
curl -X POST https://YOUR-NGROK-URL.ngrok.io/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":"test","method":"tools/list"}'
```

---

## ⚠️ **Güvenlik Considerations**

### **Riskleri:**
1. **Public Exposure:** Server'ınız internete açık
2. **Token Exposure:** Slack token'larınız risk altında
3. **Rate Limiting:** Kötüye kullanım riski
4. **Data Leakage:** Hassas veriler görülebilir

### **Güvenlik Önlemleri:**

**1. IP Filtering (Paid Plan):**
```bash
ngrok http 8000 --cidr-allow 192.168.1.0/24
```

**2. Basic Auth:**
```bash
ngrok http 8000 --basic-auth "username:password"
```

**3. Environment Restrictions:**
```bash
# Sadece development token'ları kullanın
export SLACK_BOT_TOKEN="xoxb-DEV-TOKEN"
export ENVIRONMENT="development"
```

**4. Session Monitoring:**
```python
# MCP server'da IP logging
@mcp.middleware
async def log_requests(request, call_next):
    client_ip = request.headers.get("x-forwarded-for", "unknown")
    logger.info(f"Request from IP: {client_ip}")
    return await call_next(request)
```

---

## 🛠️ **Advanced Konfigürasyonlar**

### **Custom Domain (Paid Plan):**
```bash
ngrok http 8000 --hostname=my-mcp-server.ngrok.io
```

### **Configuration File:**
```yaml
# ~/.ngrok2/ngrok.yml
version: "2"
authtoken: YOUR_TOKEN
tunnels:
  mcp-server:
    proto: http
    addr: 8000
    hostname: my-mcp-server.ngrok.io
    inspect: true
    bind_tls: true
```

```bash
# Config dosyası ile başlatma
ngrok start mcp-server
```

### **Multiple Tunnels:**
```bash
# Birden fazla port için
ngrok http 8000 &
ngrok http 8001 &
ngrok http 8002 &
```

---

## 📋 **Troubleshooting**

### **❌ "ngrok not found"**
```bash
# Kurulum kontrolü
which ngrok
ngrok version

# Yeniden kurulum
brew reinstall ngrok  # macOS
```

### **❌ "Authentication failed"**
```bash
# Token kontrolü
ngrok config check

# Token yeniden ayarlama
ngrok config add-authtoken NEW_TOKEN
```

### **❌ "Tunnel connection failed"**
```bash
# Network bağlantı kontrolü
ping ngrok.io

# Firewall kontrolü
telnet ngrok.io 443
```

### **❌ "MCP endpoint not responding"**
```bash
# Local server kontrolü
curl http://localhost:8000/mcp

# Ngrok status kontrolü
curl http://localhost:4040/api/tunnels
```

### **❌ "Cursor can't connect"**
```bash
# Config syntax kontrolü
cat ~/.cursor/mcp.json | jq

# URL validation
curl -I https://YOUR-NGROK-URL.ngrok.io/mcp
```

---

## 🆚 **Ngrok vs Production Deployment**

| Özellik | Ngrok Tunnel | AWS Production |
|---------|--------------|----------------|
| **Setup Süresi** | 5 dakika | 15-20 dakika |
| **Maliyet** | Ücretsiz (limitli) | ~$5-10/ay |
| **Güvenilirlik** | Orta | Yüksek |
| **Performance** | Orta | Yüksek |
| **URL Stability** | Değişken | Sabit |
| **SSL/HTTPS** | Otomatik | Otomatik |
| **Custom Domain** | Paid plan | Evet |
| **Monitoring** | Basic | Advanced |

### **Karar Verme:**

**Ngrok Kullan:**
- ✅ Hızlı test/demo
- ✅ Geçici paylaşım
- ✅ Development aşaması
- ✅ Bütçe kısıtı

**Production Deploy Et:**
- ✅ Uzun vadeli kullanım
- ✅ Takım için sürekli erişim
- ✅ Güvenilirlik önemli
- ✅ Custom branding

---

## 🎯 **Best Practices**

### **Development Workflow:**
1. **Local Development:** `python run_server.py`
2. **Team Sharing:** `python run_server_with_ngrok.py --ngrok`
3. **Testing:** Ngrok URL ile test
4. **Production:** AWS deployment

### **Security Checklist:**
- [ ] Development token'ları kullan
- [ ] Ngrok URL'yi güvenli paylaş
- [ ] Kullanım sonrası tunnel'ı kapat
- [ ] Dashboard'u monitor et
- [ ] Rate limiting aktif
- [ ] Error handling implementasyonu

### **Performance Tips:**
- Sadece gerektiğinde ngrok kullan
- Local development için local URL tercih et
- Production deployment için AWS kullan
- Tunnel bağlantı sayısını limit et

---

## 📚 **Ek Kaynaklar**

- **Ngrok Documentation:** https://ngrok.com/docs
- **MCP Slack Server Repo:** https://github.com/bahakizil/mcp-slack-server
- **FastMCP Documentation:** https://github.com/jlowin/fastmcp
- **Cursor MCP Guide:** https://docs.cursor.sh/mcp

---

## 🆘 **Destek**

- 🐛 **Issues:** [GitHub Issues](https://github.com/bahakizil/mcp-slack-server/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/bahakizil/mcp-slack-server/discussions)
- 📧 **Ngrok Support:** support@ngrok.com

---

**🎉 Artık MCP Slack Server'ınızı ngrok ile internete açabilir ve takım arkadaşlarınızla paylaşabilirsiniz!** 