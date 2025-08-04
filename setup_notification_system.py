#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import os
import sys

# Add current directory to path
sys.path.append('.')
from app import get_db_connection

def setup_notification_system():
    """Notification sistem tablolarını ve eksik kolonları oluştur"""
    print("🚀 Setting up notification system...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Users tablosuna is_active kolonu ekle
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE')
            print("✅ users.is_active kolonu eklendi")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("ℹ️ users.is_active kolonu zaten mevcut")
            else:
                print(f"⚠️ users.is_active kolonu ekleme hatası: {e}")
        
        # 2. Notification Types tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_types (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ notification_types tablosu oluşturuldu")
        
        # 3. Notification Templates tablosu
        cursor.execute('''
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ notification_templates tablosu oluşturuldu")
        
        # 4. Notifications tablosu
        cursor.execute('''
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ notifications tablosu oluşturuldu")
        
        # 5. Password reset tokens tablosu (eğer yoksa)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token VARCHAR(255) NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used_at TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_token (token),
                INDEX idx_expires (expires_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        print("✅ password_reset_tokens tablosu oluşturuldu")
        
        # 6. Notification types'ları ekle
        notification_types = [
            ('birthday', 'Doğum günü bildirimleri'),
            ('work_anniversary', 'İş yıl dönümü bildirimleri'),
            ('promotion', 'Terfi bildirimleri'),
            ('birthday_reminder', 'Doğum günü hatırlatmaları (departman için)'),
            ('anniversary_reminder', 'İş yıl dönümü hatırlatmaları (departman için)'),
            ('welcome', 'Hoş geldin mesajları'),
            ('general_announcement', 'Genel duyurular')
        ]
        
        for name, description in notification_types:
            cursor.execute('''
                INSERT IGNORE INTO notification_types (name, description) 
                VALUES (%s, %s)
            ''', (name, description))
        print("✅ Notification types eklendi")
        
        # 7. Email template'leri ekle
        email_templates = [
            # Doğum günü email
            ('birthday', 'email', '🎉 Doğum Gününüz Kutlu Olsun!', 
             '''Sevgili {{first_name}} {{last_name}},

🎂 Bugün sizin özel gününüz! Doğum gününüzü kutluyoruz ve sizinle birlikte olmaktan gurur duyuyoruz.

Plus Kitchen ailesi olarak, yeni yaşınızın sağlık, mutluluk ve başarılarla dolu olmasını diliyoruz.

🎁 Size özel sürprizlerimiz var! Detaylar için İK departmanımızla iletişime geçebilirsiniz.

En iyi dileklerimizle,
Plus Kitchen İnsan Kaynakları'''),
            
            # İş yıl dönümü email
            ('work_anniversary', 'email', '🏆 {{years}} Yıllık İş Yıl Dönümünüz Kutlu Olsun!',
             '''Sevgili {{first_name}} {{last_name}},

🎊 Bugün Plus Kitchen ailesindeki {{years}}. yılınızı kutluyoruz!

{{hire_date}} tarihinden bugüne kadar gösterdiğiniz özveri ve katkılarınız için teşekkür ederiz. Sizinle çalışmak bizim için bir onur.

Önümüzdeki yıllarda da birlikte büyümeye ve başarılar elde etmeye devam edeceğiz.

🎁 Size özel yıl dönümü hediyeniz İK departmanımızda sizleri bekliyor!

Saygılarımızla,
Plus Kitchen Yönetimi'''),
            
            # Site içi doğum günü
            ('birthday', 'in_app', '🎉 Doğum Gününüz Kutlu Olsun!',
             'Bugün sizin özel gününüz! Plus Kitchen ailesi olarak doğum gününüzü kutluyoruz. 🎂 Size özel sürprizlerimiz İK departmanında sizleri bekliyor!'),
            
            # Site içi yıl dönümü
            ('work_anniversary', 'in_app', '🏆 {{years}} Yıllık İş Yıl Dönümünüz Kutlu Olsun!',
             'Plus Kitchen ailesindeki {{years}}. yılınızı kutluyoruz! Gösterdiğiniz özveri için teşekkürler. 🎁 Yıl dönümü hediyeniz İK departmanında sizleri bekliyor!')
        ]
        
        for type_name, channel, subject, body in email_templates:
            cursor.execute('''
                INSERT IGNORE INTO notification_templates (type_id, channel, subject, body_template)
                SELECT nt.id, %s, %s, %s
                FROM notification_types nt 
                WHERE nt.name = %s
            ''', (channel, subject, body, type_name))
        print("✅ Email template'leri eklendi")
        
        # 8. Tüm kullanıcıları aktif yap
        cursor.execute('UPDATE users SET is_active = TRUE WHERE is_active IS NULL')
        print("✅ Tüm kullanıcılar aktif yapıldı")
        
        conn.commit()
        print("🎉 Notification system başarıyla kuruldu!")
        
        # 9. Test bildirimi gönder
        print("\n📧 Test bildirimi gönderiliyor...")
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM users 
            WHERE DATE_FORMAT(birth_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d')
            AND is_active = TRUE
        ''')
        today_birthdays = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM users 
            WHERE DATE_FORMAT(hire_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d')
            AND hire_date < DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            AND is_active = TRUE
        ''')
        today_anniversaries = cursor.fetchone()[0]
        
        print(f"📊 Bugün doğum günü olan: {today_birthdays} kişi")
        print(f"📊 Bugün yıl dönümü olan: {today_anniversaries} kişi")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Hata: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    setup_notification_system()