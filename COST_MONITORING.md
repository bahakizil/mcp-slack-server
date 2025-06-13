# 💰 AWS Cost Monitoring & Safety Guide

**🎯 Amaç:** MCP Slack Server'ın AWS maliyetlerini kontrol altında tutmak

---

## 🚨 **Mevcut Durum Analizi**

### **Neden Şu Anda Para Ödemiyorsun:**

1. **🆓 AWS Free Tier**
   - Yeni hesap = 12 ay ücretsiz kullanım
   - ECR: 500 MB aylık storage
   - App Runner: Minimal kullanım limitleri

2. **📊 Düşük Kullanım**
   - 0.25 vCPU, 0.5 GB RAM (minimum)
   - Test amaçlı trafik
   - Çoğunlukla idle state

3. **💳 Kredi Kartı Gereksiz**
   - Free Tier bazı servisler için kart istemez
   - Limit aştığında warning verir

---

## ⚠️ **Risk Faktörleri**

### **1. Free Tier Bitimi (12 ay sonra)**
```
Tarih: [Hesap oluşturma tarihi + 12 ay]
Maliyet: ~$5-10/ay başlar
```

### **2. Traffic Artışı**
```
Normal: 10-50 request/gün = $0
Yoğun: 1000+ request/gün = $10-50/ay
```

### **3. Konfigürasyon Değişikliği**
```
Şu an: 0.25 vCPU, 0.5 GB = ~$2/ay
Büyük: 1 vCPU, 2 GB = ~$25/ay
```

---

## 🛡️ **Güvenlik Önlemleri**

### **1. Billing Alerts Kurulumu**
```bash
# Billing alert oluştur
aws budgets create-budget \
  --account-id YOUR-ACCOUNT-ID \
  --budget '{
    "BudgetName": "MCP-Server-Budget",
    "BudgetLimit": {
      "Amount": "10",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }'
```

### **2. Cost Explorer Monitoring**
- **AWS Console → Billing & Cost Management**
- **Cost Explorer → Daily costs**
- **Filter:** App Runner, ECR

### **3. Service Limits**
```bash
# App Runner max instance limit
aws apprunner describe-service --service-arn YOUR-SERVICE-ARN \
  --query 'Service.InstanceConfiguration.InstanceRoleArn'
```

---

## 📊 **Maliyet Takip Komutları**

### **Monthly Usage Check**
```bash
# Bu ay ne kadar harcandı
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

### **Service Breakdown**
```bash
# Hangi servis ne kadar
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

### **Daily Tracking**
```bash
# Günlük maliyet
aws ce get-cost-and-usage \
  --time-period Start=2025-01-20,End=2025-01-21 \
  --granularity DAILY \
  --metrics BlendedCost
```

---

## 🎛️ **Cost Control Actions**

### **1. Pause Service (Gece/Hafta sonu)**
```bash
# Servis durdur
aws apprunner pause-service \
  --service-arn $(aws apprunner list-services \
  --query "ServiceSummaryList[?ServiceName=='slack-mcp-server'].ServiceArn" \
  --output text)

# Servis başlat
aws apprunner resume-service \
  --service-arn $(aws apprunner list-services \
  --query "ServiceSummaryList[?ServiceName=='slack-mcp-server'].ServiceArn" \
  --output text)
```

### **2. Scale Down**
```bash
# Minimum konfigürasyon
{
  "Cpu": "0.25 vCPU",
  "Memory": "0.5 GB",
  "InstanceRoleArn": "..."
}
```

### **3. Delete Service**
```bash
# Tamamen sil (acil durum)
aws apprunner delete-service \
  --service-arn YOUR-SERVICE-ARN
```

---

## 📧 **Email Alerts Setup**

### **1. Budget Alert**
```json
{
  "BudgetName": "MCP-Daily-Budget",
  "BudgetLimit": {
    "Amount": "5",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "Service": ["Amazon Elastic Container Registry", "AWS App Runner"]
  }
}
```

### **2. CloudWatch Alarm**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "MCP-Cost-Alert" \
  --alarm-description "MCP Server cost exceeded $5" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

---

## 📱 **Monitoring Dashboard**

### **Daily Check Script**
```bash
#!/bin/bash
# daily_cost_check.sh

echo "🔍 MCP Server Daily Cost Check"
echo "============================="

# Service status
SERVICE_STATUS=$(aws apprunner describe-service \
  --service-arn YOUR-SERVICE-ARN \
  --query 'Service.Status' --output text)
echo "📊 Service Status: $SERVICE_STATUS"

# Yesterday's cost
YESTERDAY=$(date -d "yesterday" '+%Y-%m-%d')
TODAY=$(date '+%Y-%m-%d')

COST=$(aws ce get-cost-and-usage \
  --time-period Start=$YESTERDAY,End=$TODAY \
  --granularity DAILY \
  --metrics BlendedCost \
  --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
  --output text 2>/dev/null || echo "0")

echo "💰 Yesterday's Cost: $${COST}"

# Alert if > $1
if (( $(echo "$COST > 1" | bc -l) )); then
    echo "⚠️  WARNING: Daily cost exceeded $1!"
fi
```

---

## 🎯 **Recommended Actions**

### **Hemen Yap:**
1. ✅ **Budget alert** kur ($10/ay limit)
2. ✅ **Email notification** aktif et
3. ✅ **Weekly cost check** script'i çalıştır

### **Uzun Vadede:**
1. 🔄 **Monthly review** cost trends
2. 📊 **Usage optimization** based on traffic
3. 🏗️ **Architecture review** if costs grow

### **Emergency Plan:**
1. 🚨 **Pause service** immediately
2. 📧 **Check billing dashboard**
3. 🔍 **Identify cost drivers**
4. ❌ **Delete if necessary**

---

## 💡 **Pro Tips**

### **1. Free Tier Maximization**
- **500 MB ECR** storage ücretsiz
- **Always Free** services kullan (Lambda, S3 ilk 5GB)
- **Data transfer** AWS içinde ücretsiz

### **2. Smart Scheduling**
```bash
# Crontab ile otomatik pause/resume
# Gece 00:00 pause
0 0 * * * /usr/local/bin/pause_mcp.sh

# Sabah 08:00 resume  
0 8 * * * /usr/local/bin/resume_mcp.sh
```

### **3. Cost-Effective Architecture**
- **Lambda + API Gateway** alternatifi
- **Static hosting** S3 + CloudFront
- **Serverless** approach consideration

---

## 📈 **Growth Planning**

### **Traffic Scenarios:**
| Requests/Day | Monthly Cost | Action |
|--------------|--------------|---------|
| < 100 | $0-2 | Free tier OK |
| 100-1K | $2-10 | Monitor closely |  
| 1K-10K | $10-50 | Optimize config |
| 10K+ | $50+ | Consider alternatives |

### **Budget Stages:**
1. **$0-5:** Safe zone, monitor
2. **$5-20:** Review and optimize
3. **$20+:** Consider architecture change

---

**🎯 Sonuç:** Şu anda güvendesin ama proaktif monitoring şart! 