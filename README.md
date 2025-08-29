# fruxAI - Crawler Orchestration & Metadata Management

fruxAI, web sitelerini akıllı bir şekilde tarayan, PDF ve HTML içeriklerini işleyen ve metadata çıkaran bir crawler orchestration sistemidir.

## 📁 Proje Yapısı

```
IntegrityGuard/
├── fruxAI/                    # Ana dokümantasyon klasörü (burası)
│   ├── CURSOR_RULES.md       # Geliştirme kuralları
│   ├── FRUX_BOOTSTRAP_PROMPT.md  # Mimari dokümantasyonu
│   └── README.md             # Bu dosya
├── _services/fruxAI/          # Backend servisleri
│   ├── api/                  # FastAPI uygulaması
│   ├── worker/               # Python crawler worker
│   ├── docker-compose.yml    # Servis orkestrasyonu
│   └── README.md             # Backend dokümantasyonu
├── frontend/fruxAI-backoffice/ # Frontend uygulaması
│   ├── index.html
│   └── README.md             # Frontend dokümantasyonu
└── IntegrityGuard/           # IG ana uygulaması (ayrı proje)
```

## 🚀 Hızlı Başlangıç

### 1. Servisleri Başlatın
```bash
cd ../_services/fruxAI
docker-compose up -d
```

### 2. Kong Gateway'i Yapılandırın
```bash
cd ../_services/fruxAI
chmod +x docker/kong-setup.sh
./docker/kong-setup.sh
```

### 3. API'yi Test Edin
```bash
cd ../_services/fruxAI
python test-api.py
```

### 4. Frontend'i Açın
- Dosya yolu: `../frontend/fruxAI-backoffice/index.html`
- Tarayıcıda açın

### 5. n8n Workflow'una Erişin
- URL: http://localhost:5678
- Kullanıcı adı: `admin`
- Şifre: `fruxai_password`

## 📊 Erişim Noktaları

| Servis | URL | Açıklama |
|--------|-----|----------|
| **API** | http://localhost:8000/fruxAI/api/v1/ | REST API endpoint'leri |
| **n8n** | http://localhost:8000/n8n/ | Workflow orchestration |
| **Grafana** | http://localhost:3000 | Monitoring dashboard'ları |
| **Prometheus** | http://localhost:9090 | Metrics collection |
| **Direct API** | http://localhost:8001/fruxAI/api/v1/ | Kong olmadan direkt erişim |

## 🎯 Ana Özellikler

- **Akıllı Crawling**: Rate limiting, robots.txt desteği, exponential backoff
- **Çoklu Format Desteği**: PDF ve HTML içeriklerini işleme
- **Metadata Extraction**: Şirket bilgileri, iletişim bilgileri, içerik analizi
- **Workflow Orchestration**: n8n ile karmaşık crawling senaryoları
- **Monitoring**: Prometheus metrics, Grafana dashboard'ları
- **Local Storage**: PDF/HTML dosyaları için organize edilmiş depolama

## 📚 Dokümantasyon

- **[Geliştirme Kuralları](CURSOR_RULES.md)**: Kodlama standartları ve mimari prensipleri
- **[Mimari Genel Bakış](FRUX_BOOTSTRAP_PROMPT.md)**: Sistem tasarımı ve bileşenler
- **[Backend API](../_services/fruxAI/README.md)**: API endpoint'leri ve kullanım
- **[Frontend Rehberi](../frontend/fruxAI-backoffice/README.md)**: Kullanıcı arayüzü dokümantasyonu

## 🛠️ Geliştirme

### Gereksinimler
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL (Supabase local veya cloud)
- Node.js (frontend için)

### Ortamı Hazırlama
```bash
# Backend servisleri
cd ../_services/fruxAI
pip install -r api/requirements.txt
pip install -r worker/requirements.txt

# Frontend
cd ../frontend/fruxAI-backoffice
npm install
```

### Test Çalıştırma
```bash
# API testleri
cd ../_services/fruxAI
python test-api.py

# Worker testleri
cd ../_services/fruxAI
python worker/main.py
```

## 🔧 Yapılandırma

### Ana Yapılandırma Dosyaları
- `_services/fruxAI/config/config.yaml` - Genel yapılandırma
- `_services/fruxAI/docker-compose.yml` - Servis orkestrasyonu
- `_services/fruxAI/docker/prometheus.yml` - Monitoring yapılandırması

### Önemli Ayarlar
```yaml
# config/config.yaml
database:
  host: "localhost"
  name: "fruxai"

crawling:
  default_rate: 1.0  # saniyede 1 istek
  respect_robots: true

kong:
  host: "localhost"
  port: 8000
```

## 📊 Monitoring ve Gözlem

### Temel Metrics
- `frux_jobs_processed_total`: İşlenen toplam job sayısı
- `frux_jobs_failed_total`: Başarısız job sayısı
- `frux_crawl_duration_seconds`: Crawl süresi
- `frux_content_size_bytes`: İçerik boyutu

### Log Dosyaları
- API logs: `_services/fruxAI/storage/logs/`
- Worker logs: Docker container logs
- n8n logs: n8n container logs

## 🤝 Katkıda Bulunma

1. Bu repo'yu fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📝 Sürüm Notları

### v1.0.0
- İlk kararlı sürüm
- Temel crawling işlevselliği
- API ve worker servisleri
- n8n workflow entegrasyonu
- Monitoring ve observability

## 📞 Destek

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Dokümantasyon**: Bu README ve bağlantılı dosyalar

---

**fruxAI** - Akıllı web crawling için modern çözüm 🚀
