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

def send_turquoise_birthday_email(to_email, first_name, last_name):
    """Turkuaz temalı doğum günü e-postası gönder"""
    
    subject = f"🎉 Doğum Gününüz Kutlu Olsun {first_name}!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #40E0D0 0%, #48D1CC 25%, #20B2AA 50%, #008B8B 75%, #006666 100%);
                min-height: 100vh; 
            }}
            .container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 20px; 
                overflow: hidden; 
                box-shadow: 0 20px 40px rgba(0,139,139,0.3);
                border: 3px solid #40E0D0;
            }}
            .header {{ 
                background: linear-gradient(135deg, #40E0D0 0%, #20B2AA 50%, #008B8B 100%); 
                color: white; 
                padding: 40px 30px; 
                text-align: center; 
                position: relative;
            }}
            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.2)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.3)"/><circle cx="40" cy="80" r="1" fill="rgba(255,255,255,0.2)"/></svg>');
            }}
            .logo {{ 
                font-size: 2rem; 
                font-weight: bold; 
                margin-bottom: 10px; 
                position: relative;
                z-index: 2;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            .content {{ 
                padding: 40px 30px; 
                background: linear-gradient(to bottom, #f0ffff 0%, #e0ffff 100%);
            }}
            .celebration {{ 
                font-size: 4rem; 
                text-align: center; 
                margin: 20px 0;
                background: linear-gradient(45deg, #40E0D0, #FF6B6B, #FFD93D);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .message {{ 
                font-size: 1.1rem; 
                line-height: 1.6; 
                color: #333; 
                margin-bottom: 20px; 
            }}
            .highlight {{ 
                background: linear-gradient(135deg, #40E0D0 0%, #20B2AA 100%); 
                color: white; 
                padding: 25px; 
                border-radius: 15px; 
                margin: 25px 0; 
                text-align: center;
                box-shadow: 0 8px 20px rgba(64,224,208,0.4);
                border: 2px solid #48D1CC;
            }}
            .highlight h3 {{
                margin-top: 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            }}
            .footer {{ 
                background: linear-gradient(135deg, #008B8B 0%, #006666 100%); 
                padding: 30px; 
                text-align: center; 
                color: white; 
            }}
            .signature {{ 
                font-weight: bold; 
                color: #40E0D0; 
                margin-top: 20px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            }}
            ul {{
                background: rgba(64,224,208,0.1);
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #40E0D0;
            }}
            li {{
                margin: 8px 0;
                color: #006666;
                font-weight: 500;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Plus Kitchen Portal</div>
                <h1>🎂 Doğum Günü Kutlaması</h1>
            </div>
            
            <div class="content">
                <div class="celebration">🎉🎈🎁</div>
                
                <div class="message">
                    <h2 style="color: #008B8B;">Sevgili {first_name} {last_name},</h2>
                    
                    <p><strong style="color: #40E0D0;">🎂 Bugün sizin özel gününüz!</strong> Plus Kitchen ailesi olarak doğum gününüzü en içten dileklerimizle kutluyoruz.</p>
                    
                    <div class="highlight">
                        <h3>🎁 Size Özel Sürprizlerimiz Var!</h3>
                        <p>Detaylar için İnsan Kaynakları departmanımızla iletişime geçebilirsiniz.</p>
                    </div>
                    
                    <p style="color: #006666; font-weight: 500;">Plus Kitchen ailesi olarak, yeni yaşınızın;</p>
                    <ul>
                        <li>🌟 Sağlık ve mutlulukla dolu olmasını</li>
                        <li>🚀 Başarılarla taçlandırılmasını</li>
                        <li>💖 Sevdiklerinizle güzel anılarla dolmasını</li>
                        <li>🌈 Her gününüzün renkli geçmesini</li>
                        <li>✨ Hayallerinizin gerçekleşmesini</li>
                    </ul>
                    <p style="color: #006666; font-weight: 500;">Diliyoruz!</p>
                    
                    <p style="color: #008B8B;">Sizinle birlikte çalışmaktan gurur duyuyoruz. Bu özel gününüzü kutlar, nice mutlu, sağlıklı yıllar dileriz!</p>
                </div>
            </div>
            
            <div class="footer">
                <div class="signature">
                    En iyi dileklerimizle,<br>
                    <strong>Plus Kitchen İnsan Kaynakları</strong><br>
                    portal.pluskitchen.com.tr
                </div>
                <p style="font-size: 0.9rem; margin-top: 20px; opacity: 0.8;">
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
            print(f"🎉 Turkuaz doğum günü e-postası başarıyla gönderildi: {to_email}")
        else:
            print(f"❌ Turkuaz doğum günü e-postası gönderilemedi: {to_email}")
        return success
    except Exception as e:
        print(f"❌ E-posta gönderme hatası: {e}")
        return False

def send_turquoise_anniversary_email(to_email, first_name, last_name, years):
    """Turkuaz temalı iş yıl dönümü e-postası gönder"""
    
    subject = f"🏆 {years} Yıllık İş Yıl Dönümünüz Kutlu Olsun {first_name}!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #40E0D0 0%, #48D1CC 25%, #20B2AA 50%, #008B8B 75%, #006666 100%);
                min-height: 100vh; 
            }}
            .container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 20px; 
                overflow: hidden; 
                box-shadow: 0 20px 40px rgba(0,139,139,0.3);
                border: 3px solid #40E0D0;
            }}
            .header {{ 
                background: linear-gradient(135deg, #40E0D0 0%, #20B2AA 50%, #008B8B 100%); 
                color: white; 
                padding: 40px 30px; 
                text-align: center; 
                position: relative;
            }}
            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><polygon points="50,10 60,40 90,40 70,60 80,90 50,75 20,90 30,60 10,40 40,40" fill="rgba(255,255,255,0.2)"/></svg>');
            }}
            .logo {{ 
                font-size: 2rem; 
                font-weight: bold; 
                margin-bottom: 10px; 
                position: relative;
                z-index: 2;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            .content {{ 
                padding: 40px 30px; 
                background: linear-gradient(to bottom, #f0ffff 0%, #e0ffff 100%);
            }}
            .celebration {{ 
                font-size: 4rem; 
                text-align: center; 
                margin: 20px 0;
                background: linear-gradient(45deg, #40E0D0, #FFD700, #FF6B6B);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .message {{ 
                font-size: 1.1rem; 
                line-height: 1.6; 
                color: #333; 
                margin-bottom: 20px; 
            }}
            .highlight {{ 
                background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                color: white; 
                padding: 25px; 
                border-radius: 15px; 
                margin: 25px 0; 
                text-align: center;
                box-shadow: 0 8px 20px rgba(255,215,0,0.4);
                border: 2px solid #FFD700;
            }}
            .highlight h3 {{
                margin-top: 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            }}
            .years-badge {{ 
                background: linear-gradient(135deg, #40E0D0, #008B8B); 
                color: white; 
                padding: 20px 30px; 
                border-radius: 50px; 
                display: inline-block; 
                margin: 20px 0; 
                font-size: 1.5rem; 
                font-weight: bold;
                box-shadow: 0 8px 20px rgba(64,224,208,0.4);
                border: 3px solid #48D1CC;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            .footer {{ 
                background: linear-gradient(135deg, #008B8B 0%, #006666 100%); 
                padding: 30px; 
                text-align: center; 
                color: white; 
            }}
            .signature {{ 
                font-weight: bold; 
                color: #40E0D0; 
                margin-top: 20px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            }}
            ul {{
                background: rgba(64,224,208,0.1);
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #40E0D0;
            }}
            li {{
                margin: 8px 0;
                color: #006666;
                font-weight: 500;
            }}
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
                    <h2 style="color: #008B8B;">Sevgili {first_name} {last_name},</h2>
                    
                    <div style="text-align: center;">
                        <div class="years-badge">{years} YIL</div>
                    </div>
                    
                    <p><strong style="color: #40E0D0;">🎊 Bugün Plus Kitchen ailesindeki {years}. yılınızı kutluyoruz!</strong></p>
                    
                    <p style="color: #006666; font-weight: 500;">Bu süreçte gösterdiğiniz;</p>
                    <ul>
                        <li>💪 <strong>Özveri ve Kararlılık</strong></li>
                        <li>🤝 <strong>Takım Çalışması</strong></li>
                        <li>🎯 <strong>Başarı Odaklı Yaklaşım</strong></li>
                        <li>🌟 <strong>Profesyonel Katkılarınız</strong></li>
                        <li>💎 <strong>Değerli Tecrübeleriniz</strong></li>
                    </ul>
                    <p style="color: #006666; font-weight: 500;">için size teşekkür ederiz.</p>
                    
                    <div class="highlight">
                        <h3>🎁 Size Özel Yıl Dönümü Hediyeniz Hazır!</h3>
                        <p>İnsan Kaynakları departmanımızda sizleri bekliyor!</p>
                    </div>
                    
                    <p style="color: #008B8B;">Sizinle çalışmak bizim için büyük bir <strong>onur</strong>. Önümüzdeki yıllarda da birlikte büyümeye, gelişmeye ve daha büyük başarılar elde etmeye devam edeceğiz.</p>
                    
                    <p style="color: #006666; font-weight: 500;">Bu anlamlı günde, Plus Kitchen ailesinin değerli bir üyesi olduğunuz için minnettarız. Nice yıllar birlikte!</p>
                </div>
            </div>
            
            <div class="footer">
                <div class="signature">
                    Saygılarımızla,<br>
                    <strong>Plus Kitchen Yönetimi</strong><br>
                    portal.pluskitchen.com.tr
                </div>
                <p style="font-size: 0.9rem; margin-top: 20px; opacity: 0.8;">
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
            print(f"🏆 Turkuaz iş yıl dönümü e-postası başarıyla gönderildi: {to_email}")
        else:
            print(f"❌ Turkuaz iş yıl dönümü e-postası gönderilemedi: {to_email}")
        return success
    except Exception as e:
        print(f"❌ E-posta gönderme hatası: {e}")
        return False

def main():
    """Ana fonksiyon - Turkuaz temalı test e-postaları gönder"""
    print("🎯 Turkuaz temalı e-postalar gönderiliyor...")
    print("=" * 60)
    
    # Test edilecek kişiler
    recipients = [
        {"email": "ali.kok@pluskitchen.com.tr", "first_name": "Ali", "last_name": "Kök", "years": 5},
        {"email": "yeliz.ay@pluskitchen.com.tr", "first_name": "Yeliz", "last_name": "Ay", "years": 3}
    ]
    
    total_success = 0
    total_emails = 0
    
    for person in recipients:
        print(f"\n🎨 {person['first_name']} {person['last_name']} için turkuaz e-postalar...")
        print("-" * 40)
        
        # Doğum günü e-postası
        print("🎂 Turkuaz doğum günü e-postası gönderiliyor...")
        birthday_success = send_turquoise_birthday_email(
            person['email'], person['first_name'], person['last_name']
        )
        total_emails += 1
        if birthday_success:
            total_success += 1
        
        # İş yıl dönümü e-postası
        print("🏆 Turkuaz iş yıl dönümü e-postası gönderiliyor...")
        anniversary_success = send_turquoise_anniversary_email(
            person['email'], person['first_name'], person['last_name'], person['years']
        )
        total_emails += 1
        if anniversary_success:
            total_success += 1
        
        print(f"✅ {person['first_name']} için sonuç: {('✅' if birthday_success else '❌')} Doğum günü, {('✅' if anniversary_success else '❌')} Yıl dönümü")
    
    # Genel sonuç raporu
    print("\n" + "=" * 60)
    print("🎨 TURKUAZ TEMA SONUÇ RAPORU:")
    print(f"📊 Toplam gönderilen e-posta: {total_success}/{total_emails}")
    print(f"📈 Başarı oranı: {(total_success/total_emails)*100:.1f}%")
    
    if total_success == total_emails:
        print("\n🎉 Tüm turkuaz temalı e-postalar başarıyla gönderildi!")
        print("📧 E-posta kutularını kontrol edebilirsiniz.")
        print("🎨 Yeni turkuaz tema aktif!")
    else:
        print("\n⚠️ Bazı e-postalar gönderilemedi. SMTP ayarlarını kontrol edin.")

if __name__ == '__main__':
    main()