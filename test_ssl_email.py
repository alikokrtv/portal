#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_service import email_service

def test_ssl_email():
    """SSL ile türkçe karakterli email testi"""
    
    print("🔒 SSL Email Servisi Test Ediliyor...")
    print("=" * 50)
    
    # Test parametreleri
    to_email = "ali.kok@pluskitchen.com.tr"
    subject = "🚀 SSL Test - Türkçe Karakter Testi"
    
    # Türkçe karakterli HTML içerik
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
            .content { padding: 30px; }
            .footer { background-color: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }
            .test-box { background-color: #e8f5e8; border: 2px solid #4caf50; padding: 15px; border-radius: 8px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 SSL Email Test</h1>
                <p>Port 465 ile SSL Bağlantı Testi</p>
            </div>
            <div class="content">
                <h2>Merhaba Ali Bey! 👋</h2>
                
                <div class="test-box">
                    <h3>📧 Email Servisi Başarıyla Güncellendi!</h3>
                    <ul>
                        <li>✅ SSL bağlantısı aktif (Port 465)</li>
                        <li>✅ Türkçe karakter desteği çalışıyor</li>
                        <li>✅ UTF-8 encoding doğru</li>
                        <li>✅ SMTP_SSL kullanılıyor</li>
                    </ul>
                </div>
                
                <h3>🧪 Türkçe Karakter Testi:</h3>
                <p><strong>Büyük harfler:</strong> ÇĞİÖŞÜ</p>
                <p><strong>Küçük harfler:</strong> çğıöşü</p>
                <p><strong>Özel karakterler:</strong> €₺@#$%&*()+=[]{}|\\:";'<>?,./</p>
                
                <h3>📊 Teknik Detaylar:</h3>
                <ul>
                    <li><strong>SMTP Server:</strong> mail.kurumsaleposta.com</li>
                    <li><strong>Port:</strong> 465 (SSL)</li>
                    <li><strong>Gönderen:</strong> portal.pluskitchen.com.tr</li>
                    <li><strong>Encoding:</strong> UTF-8</li>
                    <li><strong>Tarih:</strong> 28 Temmuz 2025, 17:30</li>
                </ul>
                
                <p>Bu email başarıyla ulaştıysa, SSL konfigürasyonu ve türkçe karakter desteği tam olarak çalışıyor demektir! 🎉</p>
            </div>
            <div class="footer">
                <p><strong>Plus Kitchen Portal</strong><br>
                SSL Email Test Sistemi</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text versiyonu
    plain_content = """
    SSL Email Test - Türkçe Karakter Testi
    =====================================
    
    Merhaba Ali Bey!
    
    Email servisi başarıyla SSL ile güncellendi:
    
    ✅ SSL bağlantısı aktif (Port 465)
    ✅ Türkçe karakter desteği çalışıyor
    ✅ UTF-8 encoding doğru
    ✅ SMTP_SSL kullanılıyor
    
    Türkçe Karakter Testi:
    - Büyük harfler: ÇĞİÖŞÜ
    - Küçük harfler: çğıöşü
    
    Teknik Detaylar:
    - SMTP Server: mail.kurumsaleposta.com
    - Port: 465 (SSL)
    - Gönderen: portal.pluskitchen.com.tr
    - Encoding: UTF-8
    - Tarih: 28 Temmuz 2025, 17:30
    
    Bu email başarıyla ulaştıysa, SSL konfigürasyonu tam olarak çalışıyor!
    
    Plus Kitchen Portal
    SSL Email Test Sistemi
    """
    
    print(f"📧 Alıcı: {to_email}")
    print(f"📝 Konu: {subject}")
    print(f"🔒 SSL Port: 465")
    print(f"🌐 Encoding: UTF-8")
    print("-" * 50)
    
    # Email gönder
    try:
        result = email_service.send_email(to_email, subject, html_content, plain_content)
        
        if result:
            print("\n🎉 TEST BAŞARILI!")
            print("✅ SSL email başarıyla gönderildi")
            print("✅ Türkçe karakterler destekleniyor")
            print("✅ Port 465 çalışıyor")
            print("\n📬 Lütfen gelen kutunuzu kontrol edin!")
        else:
            print("\n❌ TEST BAŞARISIZ!")
            print("Email gönderilemedi")
            
    except Exception as e:
        print(f"\n💥 HATA: {e}")
        print("SSL bağlantısı başarısız olabilir")

if __name__ == "__main__":
    test_ssl_email()
