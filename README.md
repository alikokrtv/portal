# Plus Kitchen Portal

Modern ve kullanıcı dostu bir kurumsal iletişim portalı.

## Özellikler

- 🔐 Güvenli kullanıcı girişi
- 📢 Duyuru yönetimi
- 💬 Mesajlaşma sistemi
- 👥 Kullanıcı yönetimi
- 📊 İstatistik dashboard'u
- 📱 Responsive tasarım
- 🎨 Modern Bootstrap 5 arayüzü

## Kurulum

### Gereksinimler

- Python 3.8+
- SQLite (varsayılan olarak dahil)

### Adımlar

1. **Projeyi klonlayın:**
   ```bash
   git clone <repository_url>
   cd plus_kitchen_portal
   ```

2. **Sanal ortam oluşturun:**
   ```bash
   python -m venv venv
   
   # Windows için:
   venv\Scripts\activate
   
   # Linux/Mac için:
   source venv/bin/activate
   ```

3. **Gerekli paketleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Uygulamayı çalıştırın:**
   ```bash
   python app.py
   ```

5. **Tarayıcıda açın:**
   ```
   http://localhost:6600
   ```

## Varsayılan Giriş Bilgileri

- **Kullanıcı Adı:** admin
- **Şifre:** admin123

## Teknolojiler

- **Backend:** Flask, SQLite, SQLAlchemy
- **Frontend:** Bootstrap 5, JavaScript
- **Güvenlik:** Werkzeug (şifre hashleme), Flask sessions
- **Veritabanı:** SQLite (geliştirme için ideal)

## Proje Yapısı

```
plus_kitchen_portal/
├── app.py              # Ana uygulama dosyası
├── requirements.txt    # Python bağımlılıkları
├── database.db         # SQLite veritabanı (otomatik oluşur)
├── templates/          # Jinja2 şablonları
│   ├── base.html       # Ana şablon
│   ├── login.html      # Giriş sayfası
│   ├── dashboard.html  # Ana sayfa
│   ├── announcements.html
│   ├── messages.html
│   └── users.html
└── README.md          # Bu dosya
```

## API Endpoints

- `GET /` - Ana sayfa (dashboard'a yönlendirir)
- `GET/POST /login` - Kullanıcı girişi
- `GET /logout` - Çıkış
- `GET /dashboard` - Ana sayfa
- `GET /announcements` - Duyurular
- `POST /announcements/create` - Yeni duyuru
- `GET /messages` - Mesajlar
- `POST /messages/send` - Mesaj gönder
- `GET /users` - Kullanıcılar
- `GET /api/messages/unread/count` - Okunmamış mesaj sayısı
- `POST /api/messages/<id>/read` - Mesajı okundu işaretle

## Geliştirme

Geliştirme modunda çalıştırmak için:

```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

## Güvenlik

- Şifreler Werkzeug ile hashlenir
- Session tabanlı kimlik doğrulama
- SQL injection koruması (parametreli sorgular)
- XSS koruması (Jinja2 otomatik escaping)

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Destek

Herhangi bir sorun yaşarsanız, lütfen GitHub issues bölümünde bildirin. 