# Plus Kitchen Portal 🏢

Modern, tam kapsamlı intranet sistemi - Flask tabanlı kurumsal iletişim ve yönetim platformu.

## ✨ Özellikler

### 🎯 Ana Dashboard
- **Modern Widget'lar**: Gradyan renkli istatistik kartları
- **Merkez Duyurular**: Ana odak noktası olarak duyuru akışı
- **Sağ Panel**: Yaklaşan doğum günleri ve iş yıl dönümleri
- **Departman Durumu**: Genel organizasyon görünümü
- **Hızlı İşlemler**: Tek tıkla yeni duyuru ve mesaj

### 👥 Personel Yönetimi
- **Kullanıcı Yönetimi**: Tam kapsamlı CRUD işlemleri
- **Departman Organizasyonu**: Hiyerarşik yapı yönetimi
- **Profil Sistemleri**: Detaylı kişisel bilgiler
- **Yetki Kontrolleri**: Güvenli erişim yönetimi

### 📢 İletişim Araçları
- **Duyuru Sistemi**: Merkezi bilgilendirme
- **Mesajlaşma**: Kullanıcılar arası iletişim
- **Görev Yönetimi**: Atama ve takip sistemi
- **Doküman Paylaşımı**: Merkezi dosya yönetimi

### 📊 Analiz ve Raporlama
- **Detaylı Raporlar**: Kullanıcı ve departman analizi
- **İstatistikler**: Gerçek zamanlı sistem durumu
- **Dışa Aktarma**: Excel, PDF, CSV formatları
- **Grafik Gösterimler**: Trend analizi

### 🎉 Özel Günler
- **Doğum Günü Takibi**: Otomatik hatırlatmalar
- **İş Yıl Dönümleri**: Hizmet süresi gösterimi
- **Kutlama Sistemi**: Özel gün bildirimleri

## 🚀 Uzak Sunucu Kurulumu

### Gereksinimler
```bash
- Python 3.8+
- MySQL 8.0+
- Linux/Ubuntu Server
- 1GB+ RAM
- 5GB+ Disk Alanı
```

### 1. Sunucuya Dosyaları Yükle
```bash
# Projeyi sunucuya kopyala
scp -r plus_kitchen_portal/ user@your-server:/var/www/
```

### 2. Sunucuda Kurulum
```bash
# Sunucuya bağlan
ssh user@your-server

# Proje dizinine git
cd /var/www/plus_kitchen_portal

# Deployment script'ini çalıştır
chmod +x deploy.sh
./deploy.sh
```

### 3. Database Ayarları
```bash
# MySQL'e bağlan
mysql -u root -p

# Database oluştur
CREATE DATABASE corporate_communicator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Kullanıcı oluştur
CREATE USER 'plus_kitchen'@'localhost' IDENTIFIED BY 'güçlü-şifre';
GRANT ALL PRIVILEGES ON corporate_communicator.* TO 'plus_kitchen'@'localhost';
FLUSH PRIVILEGES;

# Tabloları import et
mysql -u root -p corporate_communicator < gg.sql
```

### 4. Environment Ayarları
```bash
# .env dosyasını düzenle
nano .env
```

```env
# Database ayarları - production için
DB_HOST=localhost
DB_USER=plus_kitchen
DB_PASSWORD=güçlü-şifre
DB_NAME=corporate_communicator
DB_PORT=3306

# Güvenlik
SECRET_KEY=çok-güçlü-secret-key-burada
FLASK_ENV=production
FLASK_DEBUG=False
```

### 5. Nginx Yapılandırması (Opsiyonel)
```nginx
# /etc/nginx/sites-available/plus_kitchen
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:6600;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. Systemd Service (Opsiyonel)
```ini
# /etc/systemd/system/plus-kitchen.service
[Unit]
Description=Plus Kitchen Portal
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/plus_kitchen_portal
Environment=PATH=/var/www/plus_kitchen_portal/venv/bin
ExecStart=/var/www/plus_kitchen_portal/venv/bin/gunicorn --bind 0.0.0.0:6600 --workers 4 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Service'i aktifleştir
sudo systemctl enable plus-kitchen
sudo systemctl start plus-kitchen
sudo systemctl status plus-kitchen
```

## 🔧 Manuel Çalıştırma

### Geliştirme Ortamı
```bash
# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı başlat
python app.py
```

### Production Ortamı
```bash
# Gunicorn ile çalıştır
gunicorn --bind 0.0.0.0:6600 --workers 4 app:app
```

## 📱 Kullanım

### Erişim
- **URL**: `http://your-server-ip:6600`
- **Varsayılan Giriş**: Database'den kullanıcı oluşturun

### Özellik Rehberi

#### 🏠 Ana Dashboard
- **İstatistik Kartları**: Personel, departman, duyuru, mesaj sayıları
- **Duyuru Akışı**: Son 5 duyuru ortada görüntülenir
- **Doğum Günleri**: Yaklaşan 30 gün içindeki doğum günleri
- **Yıl Dönümleri**: İş yıl dönümleri ve hizmet süreleri
- **Hızlı İşlemler**: Modal'lar ile hızlı ekleme

#### 👥 Personel Yönetimi
- **Kullanıcı Ekleme**: Form ile yeni personel kaydı
- **Departman Atama**: Dropdown ile departman seçimi
- **Profil Görüntüleme**: Detaylı kişisel bilgiler
- **Arama**: Anlık filtreleme

#### 📢 Duyuru Sistemi
- **Yeni Duyuru**: Başlık ve içerik ile oluşturma
- **Kategori**: Otomatik kategorizasyon
- **Yazar Bilgisi**: Oluşturan kişi gösterimi
- **Tarih**: Otomatik zaman damgası

#### 💬 Mesajlaşma
- **Kişisel Mesajlar**: Birebir iletişim
- **Konu Başlığı**: Organize edilmiş konuşmalar
- **Okundu Bilgisi**: Mesaj durumu takibi
- **Bildirimler**: Okunmamış mesaj sayacı

#### 📊 Raporlar
- **Kullanıcı İstatistikleri**: Departman bazlı dağılım
- **Aktivite Analizi**: Kullanım trendleri
- **Dışa Aktarma**: Excel, PDF, CSV formatları
- **Grafikler**: Görsel analiz araçları

## 🛠️ Teknoloji Stack

### Backend
- **Flask 3.0**: Python web framework
- **PyMySQL**: MySQL bağlantısı
- **Werkzeug**: Güvenlik araçları
- **python-dotenv**: Environment yönetimi
- **Gunicorn**: Production server

### Frontend
- **Bootstrap 5.3**: Modern UI framework
- **Bootstrap Icons**: İkon seti
- **Vanilla JavaScript**: İnteraktif özellikler
- **CSS Custom Properties**: Tema sistemi

### Database
- **MySQL 8.0**: İlişkisel veritabanı
- **utf8mb4**: Türkçe karakter desteği
- **Foreign Keys**: Veri bütünlüğü

## 🔐 Güvenlik

- **Session Yönetimi**: Flask secure sessions
- **Password Hashing**: Werkzeug güvenli hash
- **SQL Injection Koruması**: Parameterized queries
- **XSS Koruması**: Template escaping
- **Environment Variables**: Sensitive data koruması

## 📈 Performans

- **Gunicorn Workers**: Multi-process handling
- **Connection Pooling**: Database optimizasyonu
- **Static File Caching**: CDN ready
- **Lazy Loading**: Büyük veri setleri için

## 🐛 Sorun Giderme

### Database Bağlantı Hatası
```bash
# MySQL servisini kontrol et
sudo systemctl status mysql

# .env dosyası ayarlarını kontrol et
cat .env
```

### Port Çakışması
```bash
# Port kullanımını kontrol et
netstat -tlnp | grep :6600

# Farklı port kullan
export PORT=8080
python app.py
```

### Performans Sorunları
```bash
# Log dosyalarını kontrol et
tail -f logs/error.log
tail -f logs/access.log

# Sistem kaynaklarını monitör et
htop
```

## 📞 Destek

### Log Dosyaları
- **Access Log**: `logs/access.log`
- **Error Log**: `logs/error.log`
- **Application Log**: Console output

### Yaygın Hatalar
1. **Unicode Error**: .env dosyası encoding sorunu
2. **Database Connection**: MySQL ayarları
3. **Permission Denied**: Dosya izinleri

## 🚀 Gelecek Güncellemeler

- [ ] Email bildirimleri
- [ ] Mobile responsive geliştirmeleri
- [ ] API endpoints
- [ ] Dashboard widget'ları özelleştirme
- [ ] Bulk operations
- [ ] Advanced reporting

---

**Plus Kitchen Portal** - Modern intranet çözümü, tam kapsamlı kurumsal iletişim platformu.

💡 **İpucu**: Uzak sunucuda çalıştırmadan önce tüm environment variables'ları kontrol edin! 