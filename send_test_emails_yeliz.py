#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

try:
    from email_service import email_service
    print("✅ Email service imported successfully")
except ImportError as e:
    print(f"❌ Failed to import email service: {e}")
    sys.exit(1)

def send_birthday_email_to_yeliz():
    """Yeliz Ay'a doğum günü e-postası gönder"""
    
    to_email = "yeliz.ay@pluskitchen.com.tr"
    subject = "🎉 Doğum Gününüz Kutlu Olsun Yeliz Hanım!"
    
    html_content = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 50%, #FECFEF 100%); min-height: 100vh; }
            .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
            .header { background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%); color: white; padding: 40px 30px; text-align: center; }
            .logo { font-size: 2rem; font-weight: bold; margin-bottom: 10px; }
            .content { padding: 40px 30px; }
            .celebration { font-size: 4rem; text-align: center; margin: 20px 0; }
            .message { font-size: 1.1rem; line-height: 1.6; color: #333; margin-bottom: 20px; }
            .highlight { background: linear-gradient(135deg, #FFB6C1, #FF69B4); color: white; padding: 20px; border-radius: 15px; margin: 20px 0; text-align: center; }
            .footer { background: #f8f9fa; padding: 30px; text-align: center; color: #666; }
            .signature { font-weight: bold; color: #FF69B4; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Plus Kitchen Portal</div>
                <h1>🎂 Doğum Günü Kutlaması</h1>
            </div>
            
            <div class="content">
                <div class="celebration">🎉🌸🎁</div>
                
                <div class="message">
                    <h2>Sevgili Yeliz Hanım,</h2>
                    
                    <p><strong>🎂 Bugün sizin özel gününüz!</strong> Plus Kitchen ailesi olarak doğum gününüzü en içten dileklerimizle kutluyoruz.</p>
                    
                    <div class="highlight">
                        <h3>🎁 Size Özel Sürprizlerimiz Var!</h3>
                        <p>Detaylar için İnsan Kaynakları departmanımızla iletişime geçebilirsiniz.</p>
                    </div>
                    
                    <p>Plus Kitchen ailesi olarak, yeni yaşınızın;</p>
                    <ul>
                        <li>🌟 Sağlık ve mutlulukla dolu olmasını</li>
                        <li>🌺 Güzelliklerle süslenmesini</li>
                        <li>💖 Sevdiklerinizle güzel anılarla dolmasını</li>
                        <li>🌈 Her gününüzün renkli geçmesini</li>
                        <li>✨ Hayallerinizin gerçekleşmesini</li>
                    </ul>
                    <p>Diliyoruz!</p>
                    
                    <p>Sizinle birlikte çalışmaktan mutluluk duyuyoruz. Bu özel gününüzü kutlar, nice mutlu, sağlıklı yıllar dileriz!</p>
                </div>
            </div>
            
            <div class="footer">
                <div class="signature">
                    En iyi dileklerimizle,<br>
                    <strong>Plus Kitchen İnsan Kaynakları</strong><br>
                    portal.pluskitchen.com.tr
                </div>
                <p style="font-size: 0.9rem; margin-top: 20px;">
                    Bu otomatik bir e-postadır. Plus Kitchen Portal sistemi tarafından gönderilmiştir.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        success = email_service.send_email(to_email, subject, html_content)
        if success:
            print(f"🎉 Doğum günü e-postası başarıyla gönderildi: {to_email}")
        else:
            print(f"❌ Doğum günü e-postası gönderilemedi: {to_email}")
        return success
    except Exception as e:
        print(f"❌ E-posta gönderme hatası: {e}")
        return False

def send_anniversary_email_to_yeliz():
    """Yeliz Ay'a iş yıl dönümü e-postası gönder"""
    
    to_email = "yeliz.ay@pluskitchen.com.tr"
    subject = "🏆 3 Yıllık İş Yıl Dönümünüz Kutlu Olsun Yeliz Hanım!"
    
    html_content = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }
            .logo { font-size: 2rem; font-weight: bold; margin-bottom: 10px; }
            .content { padding: 40px 30px; }
            .celebration { font-size: 4rem; text-align: center; margin: 20px 0; }
            .message { font-size: 1.1rem; line-height: 1.6; color: #333; margin-bottom: 20px; }
            .highlight { background: linear-gradient(135deg, #FFD700, #FFA500); color: white; padding: 20px; border-radius: 15px; margin: 20px 0; text-align: center; }
            .years-badge { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 15px 25px; border-radius: 50px; display: inline-block; margin: 20px 0; font-size: 1.3rem; font-weight: bold; }
            .footer { background: #f8f9fa; padding: 30px; text-align: center; color: #666; }
            .signature { font-weight: bold; color: #667eea; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Plus Kitchen Portal</div>
                <h1>🏆 İş Yıl Dönümü Kutlaması</h1>
            </div>
            
            <div class="content">
                <div class="celebration">🎊🏆🌟</div>
                
                <div class="message">
                    <h2>Sevgili Yeliz Hanım,</h2>
                    
                    <div style="text-align: center;">
                        <div class="years-badge">3 YIL</div>
                    </div>
                    
                    <p><strong>🎊 Bugün Plus Kitchen ailesindeki 3. yılınızı kutluyoruz!</strong></p>
                    
                    <p>2022 yılından bugüne kadar gösterdiğiniz;</p>
                    <ul>
                        <li>💪 <strong>Azim ve Kararlılık</strong></li>
                        <li>🤝 <strong>Takım Ruhu</strong></li>
                        <li>🎯 <strong>Detay Odaklı Çalışma</strong></li>
                        <li>🌟 <strong>Değerli Katkılarınız</strong></li>
                        <li>💎 <strong>Profesyonel Yaklaşımınız</strong></li>
                    </ul>
                    <p>için size minnettarız.</p>
                    
                    <div class="highlight">
                        <h3>🎁 Size Özel Yıl Dönümü Hediyeniz Hazır!</h3>
                        <p>İnsan Kaynakları departmanımızda sizleri bekliyor!</p>
                    </div>
                    
                    <p>Sizinle çalışmak bizim için büyük bir <strong>mutluluk</strong>. Önümüzdeki yıllarda da birlikte büyümeye, gelişmeye ve daha büyük başarılar elde etmeye devam edeceğiz.</p>
                    
                    <p>Bu anlamlı günde, Plus Kitchen ailesinin değerli bir üyesi olduğunuz için teşekkür ederiz. Nice yıllar birlikte!</p>
                </div>
            </div>
            
            <div class="footer">
                <div class="signature">
                    Saygılarımızla,<br>
                    <strong>Plus Kitchen Yönetimi</strong><br>
                    portal.pluskitchen.com.tr
                </div>
                <p style="font-size: 0.9rem; margin-top: 20px;">
                    Bu otomatik bir e-postadır. Plus Kitchen Portal sistemi tarafından gönderilmiştir.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        success = email_service.send_email(to_email, subject, html_content)
        if success:
            print(f"🏆 İş yıl dönümü e-postası başarıyla gönderildi: {to_email}")
        else:
            print(f"❌ İş yıl dönümü e-postası gönderilemedi: {to_email}")
        return success
    except Exception as e:
        print(f"❌ E-posta gönderme hatası: {e}")
        return False

def main():
    """Ana fonksiyon - Yeliz Ay'a test e-postaları gönder"""
    print("🎯 Yeliz Ay'a test e-postaları gönderiliyor...")
    print("=" * 50)
    
    # Doğum günü e-postası
    print("\n🎂 Doğum günü e-postası gönderiliyor...")
    birthday_success = send_birthday_email_to_yeliz()
    
    # İş yıl dönümü e-postası
    print("\n🏆 İş yıl dönümü e-postası gönderiliyor...")
    anniversary_success = send_anniversary_email_to_yeliz()
    
    # Sonuç raporu
    print("\n" + "=" * 50)
    print("📊 SONUÇ RAPORU:")
    print(f"🎂 Doğum günü e-postası: {'✅ Başarılı' if birthday_success else '❌ Başarısız'}")
    print(f"🏆 İş yıl dönümü e-postası: {'✅ Başarılı' if anniversary_success else '❌ Başarısız'}")
    
    if birthday_success and anniversary_success:
        print("\n🎉 Tüm e-postalar başarıyla gönderildi!")
        print("📧 Yeliz Ay'ın e-posta kutusunu kontrol edebilirsiniz.")
    else:
        print("\n⚠️ Bazı e-postalar gönderilemedi. SMTP ayarlarını kontrol edin.")

if __name__ == '__main__':
    main()