# fruxAI Frontend - Backoffice Dashboard

fruxAI crawler sisteminin yönetim arayüzü.

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Modern web tarayıcısı
- Backend API (çalışır durumda olmalı)

### Kullanım
1. `index.html` dosyasını tarayıcıda açın
2. API endpoint'ini yapılandırın
3. Dashboard'ı kullanmaya başlayın

## 📊 Özellikler

- **Job Yönetimi**: Crawl job'larını oluşturma, izleme, durdurma
- **Metadata Görüntüleme**: Çıkarılan verileri görüntüleme
- **Raporlama**: İstatistikler ve analizler
- **Şirket Yönetimi**: Firma bazlı veri gruplandırma
- **Real-time Monitoring**: Canlı sistem durumu

## 🔧 Yapılandırma

### API Bağlantısı
```javascript
// api.js dosyasında
const API_BASE_URL = 'http://localhost:8000/fruxAI/api/v1';
```

### Tema ve Stil
- TailwindCSS tabanlı
- Responsive tasarım
- Dark/Light mode desteği

## 📁 Dosya Yapısı

```
fruxAI-backoffice/
├── index.html          # Ana dashboard sayfası
├── js/
│   ├── api.js         # API bağlantıları
│   └── app.js         # Uygulama mantığı
├── css/
│   └── styles.css     # Özel stiller
└── components/        # HTML bileşenleri
    ├── dashboard.html
    ├── jobs.html
    └── reports.html
```

## 🔗 Backend Bağlantısı

Frontend aşağıdaki API endpoint'lerini kullanır:

- `GET /health` - Sistem durumu
- `GET/POST /crawl-jobs` - Job yönetimi
- `GET /metadata` - Metadata görüntüleme
- `GET /reports/*` - Raporlar
- `GET /companies` - Şirket listesi

## 🛠️ Geliştirme

### Yeni Sayfa Ekleme
1. `components/` klasörüne HTML dosyası oluşturun
2. `js/app.js`'de routing ekleyin
3. Navigation'a link ekleyin

### API Entegrasyonu
```javascript
// js/api.js
async function fetchJobs() {
    const response = await fetch(`${API_BASE_URL}/crawl-jobs`);
    return await response.json();
}
```

## 📱 Responsive Tasarım

- **Desktop**: 1200px+
- **Tablet**: 768px - 1199px
- **Mobile**: 320px - 767px

## 🎨 Tema

### Renk Paleti
- Primary: `#3B82F6` (Blue)
- Success: `#10B981` (Green)
- Warning: `#F59E0B` (Amber)
- Error: `#EF4444` (Red)

### Tipografi
- Font: Inter, sans-serif
- Başlıklar: 600 weight
- İçerik: 400 weight

## 📊 Dashboard Bileşenleri

### 1. Sistem Durumu
- API bağlantı durumu
- Worker durumu
- Queue durumu

### 2. Job İstatistikleri
- Toplam job sayısı
- Başarılı/başarısız oranları
- Ortalama işleme süresi

### 3. Metadata İstatistikleri
- Toplam çıkarılan veri
- Şirket sayısı
- İçerik türleri

### 4. Son Aktiviteler
- Son tamamlanan job'lar
- Hata logları
- Sistem olayları

## 🚀 Deployment

### Lokal Geliştirme
```bash
# Dosyaları tarayıcıda açın
open index.html
```

### Web Server
```bash
# Python ile basit server
python -m http.server 8080

# Nginx yapılandırması
server {
    listen 80;
    server_name fruxai.local;
    root /path/to/fruxAI-backoffice;
    index index.html;
}
```

## 🔒 Güvenlik

- API çağrıları için CORS yapılandırması
- XSS koruması için input sanitization
- Secure headers

## 📞 Destek

- **Dokümantasyon**: Ana [fruxAI README](../../fruxAI/README.md)
- **Backend API**: [API Dokümantasyonu](../../_services/fruxAI/README.md)
- **Issues**: GitHub Issues

---

Frontend geliştirme devam ediyor... 🚧
