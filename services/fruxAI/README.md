# fruxAI - Crawler Orchestration & Metadata Management

fruxAI, web sitelerini akıllı bir şekilde tarayan, PDF ve HTML içeriklerini işleyen ve metadata çıkaran bir crawler orchestration sistemidir.

## 🚀 Özellikler

- **Akıllı Crawling**: Rate limiting, robots.txt desteği, exponential backoff
- **Çoklu Format Desteği**: PDF ve HTML içeriklerini işleme
- **Metadata Extraction**: Şirket bilgileri, iletişim bilgileri, içerik analizi
- **Workflow Orchestration**: n8n ile karmaşık crawling senaryoları
- **Monitoring**: Prometheus metrics, Grafana dashboard'ları
- **Local Storage**: PDF/HTML dosyaları için organize edilmiş depolama
- **Supabase Integration**: PostgreSQL tabanlı metadata storage

## 🏗️ Mimari

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kong Gateway  │    │   fruxAI API    │    │ fruxAI Worker   │
│   (Port: 8000)  │◄──►│   (Port: 8001)  │◄──►│  (Port: 8002)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      n8n        │    │   Supabase      │    │   Local Storage │
│  (Port: 5678)  │    │  PostgreSQL     │    │   ./storage/    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Gereksinimler

- Docker & Docker Compose
- Python 3.11+
- PostgreSQL (Supabase local veya cloud)
- 4GB+ RAM
- 10GB+ disk alanı

## 🚀 Kurulum

### 1. Clone ve Dizine Geç
```bash
cd /services/fruxAI
```

### 2. Environment Variables Ayarla
```bash
cp .env.example .env
# .env dosyasını düzenle
```

### 3. Servisleri Başlat
```bash
docker-compose up -d
```

### 4. Health Check
```bash
curl http://localhost:8001/fruxAI/api/v1/health
```

## 📖 API Kullanımı

### Crawl Job Oluştur
```bash
curl -X POST http://localhost:8001/fruxAI/api/v1/crawl-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "test-job-1",
    "url": "https://example.com",
    "priority": 1,
    "crawl_type": "full",
    "max_depth": 2
  }'
```

### Job Listesi
```bash
curl http://localhost:8001/fruxAI/api/v1/crawl-jobs
```

### Metadata Sorgula
```bash
curl http://localhost:8001/fruxAI/api/v1/metadata?company_name=ExampleCorp
```

### Raporlar
```bash
curl http://localhost:8001/fruxAI/api/v1/reports/crawl-stats
```

## 🎯 n8n Workflow Kullanımı

1. **n8n Web UI**: http://localhost:5678
2. **Username**: admin
3. **Password**: fruxai_password

### Örnek Workflow:
1. fruxAI API'den pending job'ları çek
2. URL'leri crawl et
3. Metadata çıkar
4. Sonuçları Supabase'e kaydet

## 📊 Monitoring

### Grafana Dashboard
- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: fruxai_password

### Prometheus Metrics
- **URL**: http://localhost:9090
- **Metrics Endpoint**: http://localhost:8001/metrics

### Temel Metrics:
- `frux_jobs_processed_total`: İşlenen toplam job sayısı
- `frux_jobs_failed_total`: Başarısız job sayısı
- `frux_crawl_duration_seconds`: Crawl süresi
- `frux_content_size_bytes`: İçerik boyutu

## 🗂️ Storage Yapısı

```
/app/storage/
├── pdfs/
│   └── domain/
│       └── YYYY/MM/DD/
│           └── hash.pdf
├── htmls/
│   └── domain/
│       └── YYYY/MM/DD/
│           └── hash.html
└── metadata/
    └── domain/
        └── YYYY/MM/DD/
            ├── hash_metadata.json
            └── hash.html
```

## 🔧 Yapılandırma

### Rate Limiting
```yaml
# config/config.yaml
crawling:
  default_rate: 1.0  # saniyede 1 istek
  max_depth: 2

domain_rates:
  "example.com": 0.5  # 2 saniyede 1 istek
  "google.com": 0.2   # 5 saniyede 1 istek
```

### Kong Gateway Routes
```yaml
# Kong Admin API üzerinden ekle:
POST /services
{
  "name": "fruxai-api",
  "url": "http://fruxai-api:8001"
}

POST /routes
{
  "service": "fruxai-api",
  "paths": ["/fruxAI/api/v1"]
}
```

## 🚦 Troubleshooting

### Servis Durumunu Kontrol Et
```bash
docker-compose ps
```

### Log'ları İncele
```bash
# API logs
docker-compose logs fruxai-api

# Worker logs
docker-compose logs fruxai-worker

# Tüm servisler
docker-compose logs
```

### Veritabanı Bağlantısı
```bash
# PostgreSQL'e bağlan
docker-compose exec fruxai-db psql -U postgres -d fruxai
```

### Bellek/Disk Temizliği
```bash
# Eski dosyaları temizle (30 günden eski)
docker-compose exec fruxai-worker python -c "
from worker.utils.storage import StorageManager
sm = StorageManager()
sm.cleanup_old_files(30)
"
```

## 📈 Performance Tuning

### Worker Scaling
```bash
# Multiple worker instances
docker-compose up --scale fruxai-worker=3
```

### Database Optimization
```sql
-- Index ekleme
CREATE INDEX CONCURRENTLY idx_metadata_company_name ON metadata(company_name);

-- Partitioning (büyük veri için)
CREATE TABLE metadata_y2024 PARTITION OF metadata
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### Caching
- Redis ekleyerek metadata cache'i
- CDN ile static dosyalar için

## 🔒 Security

### Environment Variables
- Tüm secret'ları environment variable olarak sakla
- .env dosyasını .gitignore'a ekle

### Network Security
- Kong Gateway ile rate limiting
- Internal network'lerde firewall

### Data Privacy
- Hassas verileri şifrele
- GDPR compliance için data retention policy

## 🤝 Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: `/docs` klasörü

---

**fruxAI** - Akıllı web crawling için modern çözüm 🚀
