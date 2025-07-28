#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSL Bypass Email Test - Python 3.13+ için SSL legacy renegotiation sorunu çözümü
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_ssl_bypass_email():
    """SSL bypass ile email gönder"""
    print("🔐 SSL Bypass Email Test")
    print("=" * 50)
    
    # SMTP ayarları (görseldeki çalışan ayarlar)
    smtp_server = "mail.kurumsaleposta.com"
    smtp_port = 465
    smtp_username = "web@beraber.com.tr"
    smtp_password = "apV6Q69@-Ll@fS5="
    sender_email = "portal@pluskitchen.com.tr"
    sender_name = "portal.pluskitchen.com.tr"
    
    # Test email
    test_email = "ali.kok@pluskitchen.com.tr"
    subject = "Plus Kitchen Portal - SSL Test"
    
    html_content = """
    <html>
    <body style="font-family: Arial, sans-serif; margin: 20px;">
        <h2 style="color: #4ECDC4;">🚀 SSL Email Test</h2>
        <p><strong>Bu test SSL 465 portu ile gönderildi!</strong></p>
        <p>Gönderen: <strong>portal@pluskitchen.com.tr</strong></p>
        <p>Alıcı: <strong>ali.kok@pluskitchen.com.tr</strong></p>
        <p>Port: <strong>465 (SSL)</strong></p>
        <p>Test zamanı: <strong>28.07.2025 17:26</strong></p>
        <hr>
        <p style="color: #666; font-size: 12px;">
            Bu otomatik bir test emailidir.<br>
            Plus Kitchen Portal Email Sistemi
        </p>
    </body>
    </html>
    """
    
    try:
        # Email mesajını oluştur
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{sender_name} <{sender_email}>"
        message["To"] = test_email
        
        # HTML içeriği ekle
        part = MIMEText(html_content, "html", "utf-8")
        message.attach(part)
        
        print(f"📧 SMTP Ayarları:")
        print(f"   Sunucu: {smtp_server}")
        print(f"   Port: {smtp_port}")
        print(f"   Kullanıcı: {smtp_username}")
        print(f"   Gönderen: {sender_email}")
        print(f"   Alıcı: {test_email}")
        print()
        
        # SSL context oluştur ve legacy renegotiation'ı etkinleştir
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Python 3.13+ için legacy renegotiation'ı etkinleştir
        try:
            context.options &= ~ssl.OP_NO_RENEGOTIATION
        except AttributeError:
            pass  # Eski Python sürümleri için
            
        print("🔐 SSL bağlantısı kuruluyor...")
        
        # SMTP_SSL bağlantısı kur
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
        server.set_debuglevel(0)  # Debug çıktısını kapat
        
        print("🔑 Giriş yapılıyor...")
        server.login(smtp_username, smtp_password)
        
        print("📤 Email gönderiliyor...")
        server.sendmail(sender_email, test_email, message.as_string())
        server.quit()
        
        print("✅ SSL Email başarıyla gönderildi!")
        print("🎉 TEST BAŞARILI - SSL 465 portu çalışıyor!")
        return True
        
    except Exception as e:
        print(f"❌ SSL Email hatası: {e}")
        print("⚠️ TEST BAŞARISIZ")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 PLUS KITCHEN PORTAL - SSL BYPASS EMAIL TEST")
    print("=" * 60)
    test_ssl_bypass_email()
    print("=" * 60)
