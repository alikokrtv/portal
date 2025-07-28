#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basit Mail Test Scripti
"""

from email_service import email_service
from datetime import datetime

def test_email_config():
    """Email konfigürasyonunu test et"""
    print("📧 Email Servis Konfigürasyonu:")
    print(f"   SMTP Sunucu: {email_service.smtp_server}")
    print(f"   SMTP Port: {email_service.smtp_port}")
    print(f"   Kullanıcı: {email_service.smtp_username}")
    print(f"   Gönderen: {email_service.sender_email}")
    print(f"   İsim: {email_service.sender_name}")

def test_send_email():
    """Test maili gönder"""
    test_email = "ali.kok@pluskitchen.com.tr"  # Test email adresi
    subject = "Plus Kitchen Portal - Test Maili"
    
    html_content = f"""
    <h2>🚀 Mail Sistemi Test</h2>
    <p><strong>Test Tarihi:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
    <p>✅ Email servisi çalışıyor!</p>
    <p>Bu test maili Plus Kitchen Portal mail sisteminin düzgün çalıştığını doğrular.</p>
    """
    
    plain_content = f"""
    Mail Sistemi Test
    
    Test Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
    ✅ Email servisi çalışıyor!
    
    Bu test maili Plus Kitchen Portal mail sisteminin düzgün çalıştığını doğrular.
    """
    
    print(f"\n📤 Test maili gönderiliyor: {test_email}")
    
    try:
        success = email_service.send_email(test_email, subject, html_content, plain_content)
        if success:
            print("✅ Test maili başarıyla gönderildi!")
            return True
        else:
            print("❌ Test maili gönderilemedi")
            return False
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 PLUS KITCHEN PORTAL - EMAIL TEST")
    print("=" * 50)
    
    # Konfigürasyon kontrolü
    test_email_config()
    
    # Test maili gönder
    result = test_send_email()
    
    print("=" * 50)
    if result:
        print("🎉 TEST BAŞARILI - Mail sistemi çalışıyor!")
    else:
        print("⚠️ TEST BAŞARISIZ - Mail sistemi kontrol edilmeli")
    print("=" * 50)
