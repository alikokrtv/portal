#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Düzeltilmiş Mail Test Scripti
"""

from email_service import email_service
from datetime import datetime

def test_simple_email():
    """Basit test maili gönder"""
    print("🧪 Mail sistemi test ediliyor...")
    
    # Test email adresi
    test_email = "ali.kok@pluskitchen.com.tr"
    subject = "Plus Kitchen Portal - Test Maili"
    
    # Basit HTML içerik
    html_content = """
    <html>
    <body style="font-family: Arial, sans-serif; margin: 20px;">
        <h2 style="color: #667eea;">🚀 Mail Sistemi Test</h2>
        <p><strong>Test Tarihi:</strong> """ + datetime.now().strftime('%d.%m.%Y %H:%M:%S') + """</p>
        <p style="color: #28a745; font-weight: bold;">✅ Email servisi çalışıyor!</p>
        <p>Bu test maili Plus Kitchen Portal mail sisteminin düzgün çalıştığını doğrular.</p>
        <hr>
        <p style="font-size: 12px; color: #666;">Plus Kitchen Portal - Otomatik Test</p>
    </body>
    </html>
    """
    
    # Plain text içerik
    plain_content = f"""
    Mail Sistemi Test
    
    Test Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
    ✅ Email servisi çalışıyor!
    
    Bu test maili Plus Kitchen Portal mail sisteminin düzgün çalıştığını doğrular.
    
    Plus Kitchen Portal - Otomatik Test
    """
    
    print(f"📤 Test maili gönderiliyor: {test_email}")
    
    try:
        success = email_service.send_email(test_email, subject, html_content, plain_content)
        if success:
            print("✅ TEST BAŞARILI - Mail sistemi çalışıyor!")
            return True
        else:
            print("❌ TEST BAŞARISIZ - Mail gönderilemedi")
            return False
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

def test_password_reset():
    """Şifre sıfırlama test maili"""
    print("\n🔐 Şifre sıfırlama test maili gönderiliyor...")
    
    test_email = "ali.kok@pluskitchen.com.tr"
    test_link = "http://portal.pluskitchen.com.tr/reset-password/test-token-123"
    test_name = "Test Kullanıcısı"
    
    try:
        success = email_service.send_password_reset_email(test_email, test_link, test_name)
        if success:
            print("✅ Şifre sıfırlama test maili başarılı!")
            return True
        else:
            print("❌ Şifre sıfırlama test maili başarısız")
            return False
    except Exception as e:
        print(f"❌ Şifre sıfırlama test hatası: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PLUS KITCHEN PORTAL - EMAIL TEST (DÜZELTME)")
    print("=" * 60)
    print(f"📅 Test Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Email servis bilgileri
    print("\n📧 Email Servis Konfigürasyonu:")
    print(f"   SMTP Sunucu: {email_service.smtp_server}")
    print(f"   SMTP Port: {email_service.smtp_port}")
    print(f"   Kullanıcı: {email_service.smtp_username}")
    print(f"   Gönderen: {email_service.sender_email}")
    
    # Test 1: Basit email
    print("\n" + "="*40)
    print("TEST 1: BASİT EMAIL")
    print("="*40)
    result1 = test_simple_email()
    
    # Test 2: Şifre sıfırlama
    print("\n" + "="*40)
    print("TEST 2: ŞİFRE SIFIRLAMA")
    print("="*40)
    result2 = test_password_reset()
    
    # Sonuç
    print("\n" + "="*60)
    print("📊 TEST SONUÇLARI")
    print("="*60)
    print(f"Basit Email Test    : {'✅ BAŞARILI' if result1 else '❌ BAŞARISIZ'}")
    print(f"Şifre Sıfırlama Test: {'✅ BAŞARILI' if result2 else '❌ BAŞARISIZ'}")
    print("="*60)
    
    if result1 and result2:
        print("🎉 TÜM TESTLER BAŞARILI! Mail sistemi tamamen çalışıyor.")
    elif result1:
        print("⚠️ Basit email çalışıyor, şifre sıfırlama kontrol edilmeli.")
    else:
        print("❌ Mail sistemi sorunlu, SSL ayarları kontrol edilmeli.")
    
    print("="*60)
