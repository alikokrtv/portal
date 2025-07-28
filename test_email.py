#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mail Sistemi Test Scripti
Plus Kitchen Portal - Email Service Test
"""

import sys
import os
from datetime import datetime

# Email service'i import et
try:
    from email_service import email_service
    print("✅ Email service başarıyla import edildi")
except ImportError as e:
    print(f"❌ Email service import hatası: {e}")
    sys.exit(1)

def test_basic_email():
    """Basit test maili gönder"""
    print("\n🧪 Basit test maili gönderiliyor...")
    
    test_email = "test@example.com"  # Buraya test email adresinizi yazın
    subject = "Plus Kitchen Portal - Test Maili"
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }
            .content { padding: 20px; border: 1px solid #ddd; border-radius: 10px; margin-top: 10px; }
            .success { color: #28a745; font-weight: bold; }
            .info { background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Plus Kitchen Portal Test</h1>
        </div>
        <div class="content">
            <h2>Mail Sistemi Test Başarılı!</h2>
            <p class="success">✅ Email servisi çalışıyor</p>
            
            <div class="info">
                <strong>Test Bilgileri:</strong><br>
                📅 Tarih: {test_date}<br>
                🕐 Saat: {test_time}<br>
                🖥️ Sunucu: mail.kurumsaleposta.com<br>
                📧 Gönderen: web@beraber.com.tr
            </div>
            
            <p>Bu test maili, Plus Kitchen Portal mail sisteminin düzgün çalıştığını doğrular.</p>
            
            <h3>Test Edilen Özellikler:</h3>
            <ul>
                <li>✅ SMTP Bağlantısı</li>
                <li>✅ SSL/TLS Güvenlik</li>
                <li>✅ HTML Email Formatı</li>
                <li>✅ Türkçe Karakter Desteği</li>
                <li>✅ Email Template Sistemi</li>
            </ul>
        </div>
    </body>
    </html>
    """.format(
        test_date=datetime.now().strftime("%d.%m.%Y"),
        test_time=datetime.now().strftime("%H:%M:%S")
    )
    
    plain_content = f"""
    Plus Kitchen Portal - Mail Sistemi Test
    
    ✅ Email servisi başarıyla çalışıyor!
    
    Test Bilgileri:
    📅 Tarih: {datetime.now().strftime("%d.%m.%Y")}
    🕐 Saat: {datetime.now().strftime("%H:%M:%S")}
    🖥️ Sunucu: mail.kurumsaleposta.com
    📧 Gönderen: web@beraber.com.tr
    
    Bu test maili, Plus Kitchen Portal mail sisteminin düzgün çalıştığını doğrular.
    
    Test Edilen Özellikler:
    ✅ SMTP Bağlantısı
    ✅ SSL/TLS Güvenlik  
    ✅ HTML Email Formatı
    ✅ Türkçe Karakter Desteği
    ✅ Email Template Sistemi
    
    Plus Kitchen Portal
    """
    
    # Test email adresini kullanıcıdan al
    print(f"📧 Test email adresi: {test_email}")
    user_input = input("Farklı bir email adresi kullanmak ister misiniz? (Enter = varsayılan kullan): ").strip()
    if user_input:
        test_email = user_input
    
    # Email gönder
    try:
        success = email_service.send_email(test_email, subject, html_content, plain_content)
        if success:
            print(f"✅ Test maili başarıyla gönderildi: {test_email}")
            return True
        else:
            print("❌ Test maili gönderilemedi")
            return False
    except Exception as e:
        print(f"❌ Test maili gönderme hatası: {e}")
        return False

def test_password_reset_email():
    """Şifre sıfırlama test maili gönder"""
    print("\n🔐 Şifre sıfırlama test maili gönderiliyor...")
    
    test_email = "test@example.com"  # Buraya test email adresinizi yazın
    test_reset_link = "http://portal.pluskitchen.com.tr/reset-password/test-token-123456"
    test_user_name = "Test Kullanıcısı"
    
    # Test email adresini kullanıcıdan al
    print(f"📧 Test email adresi: {test_email}")
    user_input = input("Farklı bir email adresi kullanmak ister misiniz? (Enter = varsayılan kullan): ").strip()
    if user_input:
        test_email = user_input
    
    # Şifre sıfırlama emaili gönder
    try:
        success = email_service.send_password_reset_email(test_email, test_reset_link, test_user_name)
        if success:
            print(f"✅ Şifre sıfırlama test maili başarıyla gönderildi: {test_email}")
            return True
        else:
            print("❌ Şifre sıfırlama test maili gönderilemedi")
            return False
    except Exception as e:
        print(f"❌ Şifre sıfırlama test maili gönderme hatası: {e}")
        return False

def test_email_service_config():
    """Email servis konfigürasyonunu test et"""
    print("\n⚙️ Email servis konfigürasyonu kontrol ediliyor...")
    
    try:
        print(f"📧 SMTP Sunucu: {email_service.smtp_server}")
        print(f"🔌 SMTP Port: {email_service.smtp_port}")
        print(f"👤 Kullanıcı Adı: {email_service.smtp_username}")
        print(f"📨 Gönderen Email: {email_service.sender_email}")
        print(f"🏷️ Gönderen İsim: {email_service.sender_name}")
        print("✅ Email servis konfigürasyonu OK")
        return True
    except Exception as e:
        print(f"❌ Email servis konfigürasyon hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("=" * 60)
    print("🚀 PLUS KITCHEN PORTAL - EMAIL SİSTEMİ TEST")
    print("=" * 60)
    print(f"📅 Test Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Test sonuçları
    test_results = []
    
    # 1. Konfigürasyon testi
    print("\n1️⃣ EMAIL SERVİS KONFIGÜRASYON TESTİ")
    config_result = test_email_service_config()
    test_results.append(("Konfigürasyon", config_result))
    
    # 2. Basit email testi
    print("\n2️⃣ BASİT EMAIL TESTİ")
    basic_result = test_basic_email()
    test_results.append(("Basit Email", basic_result))
    
    # 3. Şifre sıfırlama email testi
    print("\n3️⃣ ŞİFRE SIFIRLAMA EMAIL TESTİ")
    reset_result = test_password_reset_email()
    test_results.append(("Şifre Sıfırlama", reset_result))
    
    # Test sonuçları özeti
    print("\n" + "=" * 60)
    print("📊 TEST SONUÇLARI ÖZETİ")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name:20} : {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 TÜM TESTLER BAŞARILI! Mail sistemi çalışıyor.")
    else:
        print("⚠️ Bazı testler başarısız. Mail sistemi kontrol edilmeli.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Test sırasında beklenmeyen hata: {e}")
        sys.exit(1)
