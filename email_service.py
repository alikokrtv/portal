import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailService:
    def __init__(self):
        self.smtp_server = "mail.kurumsaleposta.com"
        self.smtp_port = 465
        self.smtp_username = "web@beraber.com.tr"
        self.smtp_password = "apV6Q69@-Ll@fS5="
        self.sender_email = "web@beraber.com.tr"
        self.sender_name = "Plus Kitchen Portal"

    def send_email(self, to_email, subject, html_content, plain_content=None):
        """
        E-posta gönder
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

            # SSL context oluştur
            context = ssl.create_default_context()

            # SMTP bağlantısı kur ve e-posta gönder
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender_email, to_email, message.as_string())

            print(f"✅ E-posta başarıyla gönderildi: {to_email}")
            return True

        except Exception as e:
            print(f"❌ E-posta gönderme hatası: {e}")
            return False

    def send_password_reset_email(self, to_email, reset_link, user_name):
        """
        Şifre sıfırlama e-postası gönder
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

# Global email service instance
email_service = EmailService() 