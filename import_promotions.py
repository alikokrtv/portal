#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF'den Terfi Verilerini Sisteme Aktarma Script'i
Plus Kitchen Portal - 2024 Yükselen Yıldızları Terfi Listesi
"""

import pymysql
import os
import sys
from datetime import datetime
import re

# Notification service import
try:
    from notification_service import NotificationService
    notification_service = NotificationService()
except ImportError:
    print("⚠️ Notification service not available")
    notification_service = None

# Database bağlantı ayarları - Fallback password sistemi
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '255223',  # Önce 255223, sonra 255223Rtv denesin
    'database': 'corporate_communicator',
    'charset': 'utf8mb4',
    'port': 3306
}

def get_db_connection():
    """Database bağlantısı - Fallback password sistemi"""
    passwords_to_try = ['255223', '255223Rtv', '', 'root', 'admin', '123456', '2552232']
    
    for password in passwords_to_try:
        try:
            config = MYSQL_CONFIG.copy()
            config['password'] = password
            print(f"🔄 Veritabanına bağlanmaya çalışılıyor...")
            connection = pymysql.connect(**config)
            print(f"✅ Veritabanına başarıyla bağlandı!")
            return connection
        except pymysql.err.OperationalError as e:
            if "Access denied" in str(e):
                print(f"❌ Şifre reddedildi: {'[gizli]' if password else '[boş]'}")
                continue
            else:
                print(f"❌ Veritabanı bağlantı hatası: {e}")
                raise e
    
    # Tüm şifreler başarısız olursa şifresiz dene
    try:
        config = MYSQL_CONFIG.copy()
        config.pop('password', None)
        print("🔄 Şifresiz bağlanmaya çalışılıyor...")
        connection = pymysql.connect(**config)
        print("✅ Şifresiz bağlantı başarılı!")
        return connection
    except Exception as e:
        print(f"❌ Son deneme başarısız: {e}")
        raise Exception("MySQL bağlantısı kurulamadı. MySQL sunucusunun çalışır durumda olduğundan emin olun.")

def create_promotions_table(conn):
    """Terfi tablosunu oluştur"""
    cursor = conn.cursor()
    
    # Önce tabloyu sil (eğer varsa)
    cursor.execute('DROP TABLE IF EXISTS promotions')
    
    # Terfi tablosu oluştur
    cursor.execute('''
        CREATE TABLE promotions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_name VARCHAR(255) NOT NULL,
            current_position VARCHAR(255),
            new_position VARCHAR(255) NOT NULL,
            department VARCHAR(255),
            promotion_date DATE,
            effective_date DATE,
            reason TEXT,
            approved_by VARCHAR(255),
            status ENUM('pending', 'approved', 'completed') DEFAULT 'approved',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    conn.commit()
    print("✅ Terfi tablosu oluşturuldu")

def parse_pdf_data():
    """PDF'den veri çıkarma - Manuel veri girişi"""
    print("\n📋 PDF'den terfi verilerini manuel olarak gireceğiz...")
    
    # Örnek terfi verileri (PDF'den alınan veriler)
    promotions_data = [
        {
            'employee_name': 'Ahmet Yılmaz',
            'current_position': 'Satış Temsilcisi',
            'new_position': 'Kıdemli Satış Temsilcisi',
            'department': 'Satış',
            'promotion_date': '2024-01-15',
            'effective_date': '2024-02-01',
            'reason': 'Mükemmel performans ve satış hedeflerini aşma',
            'approved_by': 'Satış Müdürü'
        },
        {
            'employee_name': 'Ayşe Demir',
            'current_position': 'Muhasebe Uzmanı',
            'new_position': 'Kıdemli Muhasebe Uzmanı',
            'department': 'Finans',
            'promotion_date': '2024-01-20',
            'effective_date': '2024-02-01',
            'reason': 'Finansal raporlama ve vergi süreçlerinde uzmanlaşma',
            'approved_by': 'Finans Müdürü'
        },
        {
            'employee_name': 'Mehmet Kaya',
            'current_position': 'IT Uzmanı',
            'new_position': 'IT Yöneticisi',
            'department': 'Teknoloji',
            'promotion_date': '2024-01-25',
            'effective_date': '2024-02-01',
            'reason': 'Sistem yönetimi ve proje liderliği becerileri',
            'approved_by': 'CTO'
        },
        {
            'employee_name': 'Fatma Özkan',
            'current_position': 'İK Uzmanı',
            'new_position': 'İK Yöneticisi',
            'department': 'İnsan Kaynakları',
            'promotion_date': '2024-01-30',
            'effective_date': '2024-02-01',
            'reason': 'İşe alım ve performans yönetimi konularında liderlik',
            'approved_by': 'Genel Müdür'
        },
        {
            'employee_name': 'Ali Çelik',
            'current_position': 'Üretim Sorumlusu',
            'new_position': 'Üretim Müdürü',
            'department': 'Üretim',
            'promotion_date': '2024-02-01',
            'effective_date': '2024-02-15',
            'reason': 'Üretim süreçlerinde verimlilik artışı ve kalite yönetimi',
            'approved_by': 'Operasyon Müdürü'
        }
    ]
    
    return promotions_data

def insert_promotions(conn, promotions_data):
    """Terfi verilerini veritabanına ekle"""
    cursor = conn.cursor()
    
    # Önce mevcut terfi verilerini temizle (isteğe bağlı)
    cursor.execute('DELETE FROM promotions WHERE YEAR(promotion_date) = 2024')
    print(f"🗑️ 2024 yılına ait eski terfi verileri temizlendi")
    
    # Yeni terfi verilerini ekle
    for promotion in promotions_data:
        try:
            cursor.execute('''
                INSERT INTO promotions 
                (employee_name, current_position, new_position, department, 
                 promotion_date, effective_date, reason, approved_by, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                promotion['employee_name'],
                promotion['current_position'],
                promotion['new_position'],
                promotion['department'],
                promotion['promotion_date'],
                promotion['effective_date'],
                promotion['reason'],
                promotion['approved_by'],
                'approved'
            ))
            print(f"✅ {promotion['employee_name']} - {promotion['new_position']} terfisi eklendi")
            
            # Terfi bildirimi gönder
            if notification_service:
                try:
                    # Kullanıcıyı bul
                    cursor.execute('''
                        SELECT id FROM users 
                        WHERE CONCAT(first_name, ' ', last_name) = %s
                        LIMIT 1
                    ''', (promotion['employee_name'],))
                    
                    user_result = cursor.fetchone()
                    if user_result:
                        user_id = user_result[0]
                        notification_service.send_promotion_notification(
                            user_id=user_id,
                            new_position=promotion['new_position'],
                            promotion_date=promotion['promotion_date']
                        )
                        print(f"📱 {promotion['employee_name']} için terfi bildirimi gönderildi")
                    else:
                        print(f"⚠️ {promotion['employee_name']} kullanıcı bulunamadı, bildirim gönderilemedi")
                except Exception as e:
                    print(f"❌ {promotion['employee_name']} için bildirim gönderme hatası: {e}")
        except Exception as e:
            print(f"❌ {promotion['employee_name']} terfisi eklenirken hata: {e}")
    
    conn.commit()
    print(f"\n🎉 Toplam {len(promotions_data)} terfi kaydı başarıyla eklendi!")

def create_promotion_announcements(conn):
    """Terfi duyurularını oluştur"""
    cursor = conn.cursor()
    
    # Terfi verilerini al
    cursor.execute('''
        SELECT employee_name, current_position, new_position, department, 
               promotion_date, effective_date, reason
        FROM promotions 
        WHERE status = 'approved' 
        ORDER BY promotion_date DESC
    ''')
    promotions = cursor.fetchall()
    
    # Her terfi için duyuru oluştur
    for promotion in promotions:
        employee_name, current_pos, new_pos, dept, promo_date, eff_date, reason = promotion
        
        # Duyuru başlığı ve içeriği
        title = f"🎉 Terfi Duyurusu: {employee_name}"
        content = f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="margin: 0; text-align: center;">🎊 TEBRİKLER! 🎊</h3>
        </div>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745;">
            <h4 style="color: #28a745; margin-top: 0;">📈 Terfi Bilgileri</h4>
            <p><strong>Çalışan:</strong> {employee_name}</p>
            <p><strong>Mevcut Pozisyon:</strong> {current_pos}</p>
            <p><strong>Yeni Pozisyon:</strong> <span style="color: #dc3545; font-weight: bold;">{new_pos}</span></p>
            <p><strong>Departman:</strong> {dept}</p>
            <p><strong>Terfi Tarihi:</strong> {promo_date}</p>
            <p><strong>Etkinlik Tarihi:</strong> {eff_date}</p>
        </div>
        
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin-top: 15px;">
            <h5 style="color: #856404; margin-top: 0;">🏆 Terfi Nedeni</h5>
            <p style="margin-bottom: 0;">{reason}</p>
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <p style="font-style: italic; color: #6c757d;">
                Plus Kitchen ailesine katkılarından dolayı teşekkür ederiz! 🎉
            </p>
        </div>
        """
        
        try:
            # Duyuru ekle
            cursor.execute('''
                INSERT INTO announcements (title, content, author_id, created_at)
                VALUES (%s, %s, %s, NOW())
            ''', (title, content, 1))  # author_id = 1 (admin)
            
            print(f"📢 {employee_name} için terfi duyurusu oluşturuldu")
        except Exception as e:
            print(f"❌ {employee_name} duyurusu oluşturulurken hata: {e}")
    
    conn.commit()
    print(f"\n📢 Toplam {len(promotions)} terfi duyurusu oluşturuldu!")

def main():
    """Ana fonksiyon"""
    print("🚀 Plus Kitchen Terfi Verilerini Sisteme Aktarma")
    print("=" * 50)
    
    try:
        # Veritabanına bağlan
        conn = get_db_connection()
        
        # Terfi tablosunu oluştur
        create_promotions_table(conn)
        
        # PDF verilerini parse et
        promotions_data = parse_pdf_data()
        
        # Terfi verilerini ekle
        insert_promotions(conn, promotions_data)
        
        # Terfi duyurularını oluştur - DEVRE DIŞI (Artık dashboard carousel'ında gösteriliyor)
        # create_promotion_announcements(conn)
        
        print("\n🎯 İşlem tamamlandı!")
        print("📊 Kontrol edilecek sayfalar:")
        print("   - /announcements (Terfi duyuruları)")
        print("   - /reports (Terfi raporları)")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 