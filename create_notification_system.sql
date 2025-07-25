-- Bildirim Sistemi Tabloları
-- Notification Types
CREATE TABLE IF NOT EXISTS notification_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notification Templates
CREATE TABLE IF NOT EXISTS notification_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_id INT NOT NULL,
    channel ENUM('email', 'whatsapp', 'in_app') NOT NULL,
    subject VARCHAR(255),
    body_template TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES notification_types(id) ON DELETE CASCADE,
    INDEX idx_type_channel (type_id, channel)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    channel ENUM('email', 'whatsapp', 'in_app') NOT NULL,
    status ENUM('pending', 'sent', 'failed', 'read') DEFAULT 'pending',
    scheduled_at TIMESTAMP NULL,
    sent_at TIMESTAMP NULL,
    read_at TIMESTAMP NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES notification_types(id) ON DELETE CASCADE,
    INDEX idx_user_status (user_id, status),
    INDEX idx_scheduled_status (scheduled_at, status),
    INDEX idx_channel_status (channel, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notification Settings (kullanıcı bildirim tercihleri)
CREATE TABLE IF NOT EXISTS notification_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type_id INT NOT NULL,
    email_enabled BOOLEAN DEFAULT TRUE,
    whatsapp_enabled BOOLEAN DEFAULT TRUE,
    in_app_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES notification_types(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_type (user_id, type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bildirim türlerini ekle
INSERT IGNORE INTO notification_types (name, description) VALUES
('birthday', 'Doğum günü bildirimleri'),
('work_anniversary', 'İş yıl dönümü bildirimleri'),
('promotion', 'Terfi bildirimleri'),
('birthday_reminder', 'Doğum günü hatırlatmaları (departman için)'),
('anniversary_reminder', 'İş yıl dönümü hatırlatmaları (departman için)'),
('welcome', 'Hoş geldin mesajları'),
('general_announcement', 'Genel duyurular');

-- Email şablonları
INSERT IGNORE INTO notification_templates (type_id, channel, subject, body_template) VALUES
-- Doğum günü email'i
((SELECT id FROM notification_types WHERE name = 'birthday'), 'email', 
'🎉 Doğum Gününüz Kutlu Olsun!', 
'Sevgili {{first_name}} {{last_name}},

🎂 Bugün sizin özel gününüz! Doğum gününüzü kutluyoruz ve sizinle birlikte olmaktan gurur duyuyoruz.

Plus Kitchen ailesi olarak, yeni yaşınızın sağlık, mutluluk ve başarılarla dolu olmasını diliyoruz.

🎁 Size özel sürprizlerimiz var! Detaylar için İK departmanımızla iletişime geçebilirsiniz.

En iyi dileklerimizle,
Plus Kitchen İnsan Kaynakları'),

-- İş yıl dönümü email'i  
((SELECT id FROM notification_types WHERE name = 'work_anniversary'), 'email',
'🏆 {{years}} Yıllık İş Yıl Dönümünüz Kutlu Olsun!',
'Sevgili {{first_name}} {{last_name}},

🎊 Bugün Plus Kitchen ailesindeki {{years}}. yılınızı kutluyoruz!

{{hire_date}} tarihinden bugüne kadar gösterdiğiniz özveri ve katkılarınız için teşekkür ederiz. Sizinle çalışmak bizim için bir onur.

Önümüzdeki yıllarda da birlikte büyümeye ve başarılar elde etmeye devam edeceğiz.

🎁 Size özel yıl dönümü hediyeniz İK departmanımızda sizleri bekliyor!

Saygılarımızla,
Plus Kitchen Yönetimi'),

-- Terfi email'i
((SELECT id FROM notification_types WHERE name = 'promotion'), 'email',
'🎉 Tebrikler! Yeni Pozisyonunuz: {{new_position}}',
'Sevgili {{first_name}} {{last_name}},

🎊 Terfinizi kutluyoruz! {{promotion_date}} tarihinden itibaren {{new_position}} pozisyonunda görev yapacaksınız.

Bu terfiyi başarılı performansınız ve özverinizle hak ettiniz. Yeni görevinizde de aynı başarıları göstereceğinize inanıyoruz.

📋 Yeni pozisyonunuz ile ilgili detaylar ve görev tanımınız için İK departmanımızla görüşebilirsiniz.

Tebrikler ve başarılarınızın devamını dileriz!

Plus Kitchen Yönetimi');

-- WhatsApp şablonları
INSERT IGNORE INTO notification_templates (type_id, channel, subject, body_template) VALUES
-- Doğum günü WhatsApp
((SELECT id FROM notification_types WHERE name = 'birthday'), 'whatsapp', 
NULL,
'🎉 Sevgili {{first_name}},

🎂 Doğum gününüz kutlu olsun! Plus Kitchen ailesi olarak bugün sizin özel gününüz.

🎁 Size özel sürprizlerimiz İK departmanında sizleri bekliyor!

En iyi dileklerimizle 💝
Plus Kitchen'),

-- İş yıl dönümü WhatsApp
((SELECT id FROM notification_types WHERE name = 'work_anniversary'), 'whatsapp',
NULL,
'🏆 Tebrikler {{first_name}}!

🎊 Plus Kitchen ailesindeki {{years}}. yılınızı kutluyoruz!

Gösterdiğiniz özveri için teşekkürler. Sizinle çalışmak bizim için onur.

🎁 Yıl dönümü hediyeniz İK''da sizleri bekliyor!

Plus Kitchen Yönetimi'),

-- Terfi WhatsApp  
((SELECT id FROM notification_types WHERE name = 'promotion'), 'whatsapp',
NULL,
'🎉 Harika haber {{first_name}}!

🎊 Terfinizi kutluyoruz! Yeni pozisyonunuz: {{new_position}}

Bu başarıyı hak ettiniz! Yeni görevinizde de başarılar dileriz.

📋 Detaylar için İK departmanıyla görüşebilirsiniz.

Tebrikler! 🎊
Plus Kitchen');

-- Site içi bildirim şablonları
INSERT IGNORE INTO notification_templates (type_id, channel, subject, body_template) VALUES
-- Doğum günü site içi
((SELECT id FROM notification_types WHERE name = 'birthday'), 'in_app',
'🎉 Doğum Gününüz Kutlu Olsun!',
'Bugün sizin özel gününüz! Plus Kitchen ailesi olarak doğum gününüzü kutluyoruz. 🎂 Size özel sürprizlerimiz İK departmanında sizleri bekliyor!'),

-- İş yıl dönümü site içi
((SELECT id FROM notification_types WHERE name = 'work_anniversary'), 'in_app',
'🏆 {{years}} Yıllık İş Yıl Dönümünüz Kutlu Olsun!',
'Plus Kitchen ailesindeki {{years}}. yılınızı kutluyoruz! Gösterdiğiniz özveri için teşekkürler. 🎁 Yıl dönümü hediyeniz İK departmanında sizleri bekliyor!'),

-- Terfi site içi
((SELECT id FROM notification_types WHERE name = 'promotion'), 'in_app',
'🎉 Tebrikler! Terfi Edildiniz!',
'Yeni pozisyonunuz: {{new_position}}. Bu başarıyı hak ettiniz! Yeni görevinizde de başarılar dileriz. 📋 Detaylar için İK departmanıyla görüşebilirsiniz.');

-- Departman hatırlatma şablonları
INSERT IGNORE INTO notification_templates (type_id, channel, subject, body_template) VALUES
-- Doğum günü hatırlatması (departman için)
((SELECT id FROM notification_types WHERE name = 'birthday_reminder'), 'email',
'🎂 Departmanınızda Doğum Günü Hatırlatması',
'Sevgili {{manager_name}},

{{department_name}} departmanında yarın doğum günü olan çalışanımız:

👤 {{first_name}} {{last_name}}
📅 Doğum Günü: {{birth_date}}

Lütfen departman olarak bu özel günü kutlamayı unutmayın! 🎉

Plus Kitchen İK'),

-- İş yıl dönümü hatırlatması (departman için)  
((SELECT id FROM notification_types WHERE name = 'anniversary_reminder'), 'email',
'🏆 Departmanınızda İş Yıl Dönümü Hatırlatması',
'Sevgili {{manager_name}},

{{department_name}} departmanında yarın iş yıl dönümü olan çalışanımız:

👤 {{first_name}} {{last_name}}
📅 İşe Başlama: {{hire_date}}
🎊 Yıl Dönümü: {{years}} yıl

Lütfen bu anlamlı günü departman olarak kutlamayı unutmayın!

Plus Kitchen İK'); 