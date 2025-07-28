#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alternatif Email Service - STARTTLS ile
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailServiceAlternative:
    def __init__(self):
        self.smtp_server = "mail.kurumsaleposta.com"
        self.smtp_port_ssl = 465  # SSL
        self.smtp_port_tls = 587  # STARTTLS
        self.smtp_username = "web@beraber.com.tr"
        self.smtp_password = "apV6Q69@-Ll@fS5="
        self.sender_email = "web@beraber.com.tr"
        self.sender_name = "Plus Kitchen Portal"

    def send_email_starttls(self, to_email, subject, html_content, plain_content=None):
        """
        STARTTLS ile e-posta gönder (Port 587)
        """
        try:
            # E-posta mesajını oluştur
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = to_email

            # Plain text versiyonu
            if plain_content:
                part1 = MIMEText(plain_content, "plain", "utf-8")
                message.attach(part1)

            # HTML versiyonu
            part2 = MIMEText(html_content, "html", "utf-8")
            message.attach(part2)

            # STARTTLS ile bağlantı
            server = smtplib.SMTP(self.smtp_server, self.smtp_port_tls)
            server.starttls()  # TLS'yi etkinleştir
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.sender_email, to_email, message.as_string())
            server.quit()

            print(f"✅ E-posta başarıyla gönderildi (STARTTLS): {to_email}")
            return True

        except Exception as e:
            print(f"❌ STARTTLS e-posta gönderme hatası: {e}")
            return False

    def send_email_ssl_insecure(self, to_email, subject, html_content, plain_content=None):
        """
        SSL ile e-posta gönder (Güvensiz mod - Port 465)
        """
        try:
            # E-posta mesajını oluştur
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = to_email

            # Plain text versiyonu
            if plain_content:
                part1 = MIMEText(plain_content, "plain", "utf-8")
                message.attach(part1)

            # HTML versiyonu
            part2 = MIMEText(html_content, "html", "utf-8")
            message.attach(part2)

            # SSL context oluştur - En düşük güvenlik seviyesi
            context = ssl.create_default_context()
            context.set_ciphers('DEFAULT@SECLEVEL=0')  # En düşük seviye
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            # Legacy renegotiation'ı etkinleştir
            context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT

            # SMTP bağlantısı kur ve e-posta gönder
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port_ssl, context=context) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender_email, to_email, message.as_string())

            print(f"✅ E-posta başarıyla gönderildi (SSL Insecure): {to_email}")
            return True

        except Exception as e:
            print(f"❌ SSL Insecure e-posta gönderme hatası: {e}")
            return False

    def send_email_no_ssl(self, to_email, subject, html_content, plain_content=None):
        """
        SSL olmadan e-posta gönder (Port 25 veya 587)
        """
        try:
            # E-posta mesajını oluştur
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = to_email

            # Plain text versiyonu
            if plain_content:
                part1 = MIMEText(plain_content, "plain", "utf-8")
                message.attach(part1)

            # HTML versiyonu
            part2 = MIMEText(html_content, "html", "utf-8")
            message.attach(part2)

            # SSL olmadan bağlantı
            server = smtplib.SMTP(self.smtp_server, 25)  # Port 25
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.sender_email, to_email, message.as_string())
            server.quit()

            print(f"✅ E-posta başarıyla gönderildi (No SSL): {to_email}")
            return True

        except Exception as e:
            print(f"❌ No SSL e-posta gönderme hatası: {e}")
            return False

    def test_all_methods(self, to_email, subject, html_content, plain_content=None):
        """
        Tüm bağlantı yöntemlerini test et
        """
        print("🧪 Tüm email gönderme yöntemleri test ediliyor...")
        
        methods = [
            ("STARTTLS (Port 587)", self.send_email_starttls),
            ("SSL Insecure (Port 465)", self.send_email_ssl_insecure),
            ("No SSL (Port 25)", self.send_email_no_ssl)
        ]
        
        for method_name, method_func in methods:
            print(f"\n🔄 {method_name} test ediliyor...")
            try:
                success = method_func(to_email, subject, html_content, plain_content)
                if success:
                    print(f"✅ {method_name} BAŞARILI!")
                    return method_name, True
                else:
                    print(f"❌ {method_name} başarısız")
            except Exception as e:
                print(f"❌ {method_name} hatası: {e}")
        
        return None, False

# Test fonksiyonu
def test_alternative_email():
    """Alternatif email servisini test et"""
    email_alt = EmailServiceAlternative()
    
    test_email = "ali.kok@pluskitchen.com.tr"
    subject = "Plus Kitchen Portal - Alternatif Test"
    
    html_content = """
    <html>
    <body style="font-family: Arial, sans-serif; margin: 20px;">
        <h2 style="color: #667eea;">🔧 Alternatif Email Test</h2>
        <p><strong>Bu test farklı bağlantı yöntemlerini deniyor:</strong></p>
        <ul>
            <li>STARTTLS (Port 587)</li>
            <li>SSL Insecure (Port 465)</li>
            <li>No SSL (Port 25)</li>
        </ul>
        <p style="color: #28a745;">✅ Çalışan yöntem bulundu!</p>
    </body>
    </html>
    """
    
    plain_content = """
    Alternatif Email Test
    
    Bu test farklı bağlantı yöntemlerini deniyor:
    - STARTTLS (Port 587)
    - SSL Insecure (Port 465) 
    - No SSL (Port 25)
    
    ✅ Çalışan yöntem bulundu!
    """
    
    print("=" * 60)
    print("🔧 ALTERNATİF EMAIL SERVİS TESTİ")
    print("=" * 60)
    
    working_method, success = email_alt.test_all_methods(test_email, subject, html_content, plain_content)
    
    print("\n" + "=" * 60)
    if success:
        print(f"🎉 BAŞARILI! Çalışan yöntem: {working_method}")
        print("Bu yöntemi ana email servisinizde kullanabilirsiniz.")
    else:
        print("❌ Hiçbir yöntem çalışmadı. Sunucu ayarları kontrol edilmeli.")
    print("=" * 60)

if __name__ == "__main__":
    test_alternative_email()
