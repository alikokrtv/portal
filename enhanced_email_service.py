#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Email Service - HTML Template'li Kutlama Mailleri
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

class EnhancedEmailService:
    def __init__(self):
        self.smtp_server = "mail.kurumsaleposta.com"
        self.smtp_port = 465  # SSL port
        self.smtp_username = "web@beraber.com.tr"
        self.smtp_password = "apV6Q69@-Ll@fS5="
        self.sender_email = "portal@pluskitchen.com.tr"
        self.sender_name = "portal.pluskitchen.com.tr"
        self.template_dir = "email_templates"

    def send_email(self, to_email, subject, html_content, plain_content=None):
        """
        E-posta gönder (STARTTLS ile)
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

            # SSL ile SMTP bağlantısı kur
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.sender_email, to_email, message.as_string())
            server.quit()

            print(f"✅ E-posta başarıyla gönderildi: {to_email}")
            return True

        except Exception as e:
            print(f"❌ E-posta gönderme hatası: {e}")
            return False

    def load_template(self, template_name):
        """
        HTML template dosyasını yükle
        """
        try:
            template_path = os.path.join(self.template_dir, template_name)
            with open(template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"❌ Template yükleme hatası: {e}")
            return None

    def replace_variables(self, template, variables):
        """
        Template'teki değişkenleri değiştir
        """
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            template = template.replace(placeholder, str(value))
        return template

    def send_birthday_email(self, to_email, first_name, last_name, birth_date=None):
        """
        Doğum günü kutlama maili gönder
        """
        # HTML template'i yükle
        html_template = self.load_template("birthday_template.html")
        if not html_template:
            return False

        # Değişkenleri hazırla
        variables = {
            'first_name': first_name,
            'last_name': last_name,
            'birth_date': birth_date.strftime('%d.%m.%Y') if birth_date else 'Belirtilmemiş'
        }

        # Template'i doldur
        html_content = self.replace_variables(html_template, variables)
        
        # Plain text versiyonu
        plain_content = f"""
        Sevgili {first_name} {last_name},

        🎂 Bugün sizin özel gününüz! Doğum gününüzü kutluyoruz ve sizinle birlikte olmaktan gurur duyuyoruz.

        Plus Kitchen ailesi olarak, yeni yaşınızın sağlık, mutluluk ve başarılarla dolu olmasını diliyoruz.

        🎁 Size özel sürprizlerimiz var! Detaylar için İK departmanımızla iletişime geçebilirsiniz.

        En iyi dileklerimizle,
        Plus Kitchen İnsan Kaynakları
        """

        subject = "🎉 Doğum Gününüz Kutlu Olsun!"
        
        return self.send_email(to_email, subject, html_content, plain_content)

    def send_anniversary_email(self, to_email, first_name, last_name, hire_date, years):
        """
        İş yıl dönümü kutlama maili gönder
        """
        # HTML template'i yükle
        html_template = self.load_template("anniversary_template.html")
        if not html_template:
            return False

        # Değişkenleri hazırla
        variables = {
            'first_name': first_name,
            'last_name': last_name,
            'hire_date': hire_date.strftime('%d.%m.%Y') if hire_date else 'Belirtilmemiş',
            'years': years
        }

        # Template'i doldur
        html_content = self.replace_variables(html_template, variables)
        
        # Plain text versiyonu
        plain_content = f"""
        Sevgili {first_name} {last_name},

        🎊 Bugün Plus Kitchen ailesindeki {years}. yılınızı kutluyoruz!

        {hire_date.strftime('%d.%m.%Y') if hire_date else 'İşe başlama'} tarihinden bugüne kadar gösterdiğiniz özveri ve katkılarınız için teşekkür ederiz. Sizinle çalışmak bizim için bir onur.

        Önümüzdeki yıllarda da birlikte büyümeye ve başarılar elde etmeye devam edeceğiz.

        🎁 Size özel yıl dönümü hediyeniz İK departmanımızda sizleri bekliyor!

        Saygılarımızla,
        Plus Kitchen Yönetimi
        """

        subject = f"🏆 {years} Yıllık İş Yıl Dönümünüz Kutlu Olsun!"
        
        return self.send_email(to_email, subject, html_content, plain_content)

    def send_password_reset_email(self, to_email, reset_link, user_name):
        """
        Şifre sıfırlama e-postası gönder (mevcut fonksiyon)
        """
        subject = "Plus Kitchen Portal - Şifre Sıfırlama"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 15px 30px; border-radius: 25px; font-weight: bold; margin: 20px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; color: #856404; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Şifre Sıfırlama</h1>
                </div>
                <div class="content">
                    <h2>Merhaba {user_name},</h2>
                    <p>Plus Kitchen Portal hesabınız için şifre sıfırlama talebinde bulundunuz.</p>
                    <p>Yeni şifrenizi belirlemek için aşağıdaki butona tıklayın:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Şifremi Sıfırla</a>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Güvenlik Uyarısı:</strong><br>
                        • Bu link 1 saat boyunca geçerlidir<br>
                        • Link sadece bir kez kullanılabilir<br>
                        • Bu talebi siz yapmadıysanız bu e-postayı görmezden gelin
                    </div>
                    
                    <p>Eğer buton çalışmıyorsa, aşağıdaki linki kopyalayıp tarayıcınıza yapıştırın:</p>
                    <p style="word-break: break-all; color: #666; font-size: 12px;">{reset_link}</p>
                </div>
                <div class="footer">
                    <p><strong>Plus Kitchen Portal</strong><br>
                    Bu otomatik bir e-postadır, lütfen yanıtlamayın.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_content = f"""
        Merhaba {user_name},
        
        Plus Kitchen Portal hesabınız için şifre sıfırlama talebinde bulundunuz.
        
        Yeni şifrenizi belirlemek için aşağıdaki linki kullanın:
        {reset_link}
        
        ⚠️ Bu link 1 saat boyunca geçerlidir ve sadece bir kez kullanılabilir.
        
        Bu talebi siz yapmadıysanız bu e-postayı görmezden gelin.
        
        Plus Kitchen Portal
        """
        
        return self.send_email(to_email, subject, html_content, plain_content)

# Global enhanced email service instance
enhanced_email_service = EnhancedEmailService()
