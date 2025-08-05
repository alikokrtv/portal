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

def send_modern_birthday_email(to_email, first_name, last_name, title="Sn."):
    """Modern doğum günü e-postası - Dark/Light mode uyumlu"""
    
    subject = f"🎉 Mutlu Yıllar {first_name} {last_name}!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mutlu Yıllar</title>
        <style>
            @media (prefers-color-scheme: dark) {{
                .email-container {{
                    background-color: #1a1a1a !important;
                }}
                .card-background {{
                    background-color: #2d2d2d !important;
                    border-color: #404040 !important;
                }}
            }}
            
            body {{
                margin: 0;
                padding: 20px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                border: 1px solid #e0e0e0;
            }}
            
            .header {{
                background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
                padding: 30px 20px 20px 20px;
                text-align: right;
                position: relative;
                overflow: hidden;
            }}
            
            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="25" cy="25" r="3" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="50" r="2" fill="rgba(255,255,255,0.15)"/><circle cx="50" cy="75" r="2.5" fill="rgba(255,255,255,0.1)"/></svg>');
                animation: float 20s infinite linear;
            }}
            
            @keyframes float {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            .logo {{
                color: white;
                font-size: 1.8rem;
                font-weight: 300;
                position: relative;
                z-index: 2;
                margin-bottom: 10px;
            }}
            
            .logo .plus {{
                font-weight: 700;
            }}
            
            .main-content {{
                padding: 40px 30px;
                background: #ffffff;
                text-align: center;
            }}
            
            .title {{
                font-size: 3.5rem;
                color: #2E7D32;
                margin: 20px 0;
                font-weight: 300;
                letter-spacing: 2px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }}
            
            .title .mutlu {{
                color: #333;
                font-weight: 400;
                font-style: italic;
            }}
            
            .title .yillar {{
                color: #4CAF50;
                font-weight: 700;
                display: block;
                margin-top: -10px;
            }}
            
            .name {{
                font-size: 1.8rem;
                color: #333;
                margin: 30px 0;
                font-weight: 500;
            }}
            
            .message {{
                font-size: 1.2rem;
                line-height: 1.8;
                color: #555;
                margin: 30px 0;
                font-weight: 400;
            }}
            
            .cake-section {{
                margin: 40px 0;
                position: relative;
            }}
            
            .cake {{
                font-size: 6rem;
                margin: 20px 0;
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
            }}
            
            .celebration-text {{
                font-size: 2rem;
                color: #4CAF50;
                font-weight: 600;
                margin: 20px 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            }}
            
            .wishes {{
                background: linear-gradient(135deg, #E8F5E8 0%, #F1F8E9 100%);
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
                border-left: 5px solid #4CAF50;
            }}
            
            .footer {{
                background: #f8f9fa;
                padding: 30px;
                text-align: center;
                color: #666;
                border-top: 1px solid #e0e0e0;
            }}
            
            .company-name {{
                color: #4CAF50;
                font-weight: 600;
                font-size: 1.1rem;
            }}
            
            .decorative-elements {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                overflow: hidden;
            }}
            
            .leaf {{
                position: absolute;
                color: rgba(76, 175, 80, 0.3);
                font-size: 2rem;
                animation: sway 3s ease-in-out infinite;
            }}
            
            .leaf1 {{ top: 10%; left: 5%; animation-delay: 0s; }}
            .leaf2 {{ top: 20%; right: 8%; animation-delay: 1s; }}
            .leaf3 {{ bottom: 15%; left: 10%; animation-delay: 2s; }}
            .leaf4 {{ bottom: 25%; right: 5%; animation-delay: 0.5s; }}
            
            @keyframes sway {{
                0%, 100% {{ transform: rotate(-5deg) translateY(0px); }}
                50% {{ transform: rotate(5deg) translateY(-10px); }}
            }}
            
            /* Dark mode adjustments */
            @media (prefers-color-scheme: dark) {{
                .main-content {{
                    background-color: #2d2d2d !important;
                    color: #e0e0e0 !important;
                }}
                .name {{
                    color: #e0e0e0 !important;
                }}
                .message {{
                    color: #c0c0c0 !important;
                }}
                .title .mutlu {{
                    color: #e0e0e0 !important;
                }}
                .wishes {{
                    background: linear-gradient(135deg, #1a3a1a 0%, #2a4a2a 100%) !important;
                    color: #e0e0e0 !important;
                }}
                .footer {{
                    background-color: #1a1a1a !important;
                    color: #a0a0a0 !important;
                    border-top-color: #404040 !important;
                }}
            }}
            
            /* Mobile responsiveness */
            @media (max-width: 600px) {{
                .email-container {{
                    margin: 10px;
                    border-radius: 15px;
                }}
                .title {{
                    font-size: 2.5rem;
                }}
                .cake {{
                    font-size: 4rem;
                }}
                .main-content {{
                    padding: 30px 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">
                    <span class="plus">plus</span> Kitchen
                </div>
            </div>
            
            <div class="main-content">
                <div class="decorative-elements">
                    <div class="leaf leaf1">🌿</div>
                    <div class="leaf leaf2">🍃</div>
                    <div class="leaf leaf3">🌱</div>
                    <div class="leaf leaf4">🌿</div>
                </div>
                
                <div class="title">
                    <span class="mutlu">Mutlu</span>
                    <span class="yillar">YILLAR</span>
                </div>
                
                <div class="name">{title} {first_name} {last_name}</div>
                
                <div class="wishes">
                    <div class="message">
                        Sizinle çalışmak büyük bir keyif.<br>
                        Yeni yaşınız sağlık, mutluluk ve<br>
                        başarılarla dolu olmasını diliyoruz.
                    </div>
                </div>
                
                <div class="cake-section">
                    <div class="cake">🎂</div>
                    <div class="celebration-text">İyi ki doğdunuz.</div>
                </div>
            </div>
            
            <div class="footer">
                <div class="company-name">Plus Kitchen İnsan Kaynakları</div>
                <div style="margin-top: 10px; font-size: 0.9rem;">
                    portal.pluskitchen.com.tr
                </div>
                <div style="margin-top: 15px; font-size: 0.8rem; opacity: 0.7;">
                    Bu otomatik bir e-postadır. Plus Kitchen Portal sistemi tarafından gönderilmiştir.
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        success = email_service.send_email(to_email, subject, html_content)
        if success:
            print(f"🎉 Modern doğum günü e-postası başarıyla gönderildi: {to_email}")
        else:
            print(f"❌ Modern doğum günü e-postası gönderilemedi: {to_email}")
        return success
    except Exception as e:
        print(f"❌ E-posta gönderme hatası: {e}")
        return False

def send_modern_anniversary_email(to_email, first_name, last_name, years, title="Sn."):
    """Modern iş yıl dönümü e-postası - Dark/Light mode uyumlu"""
    
    subject = f"🏆 {years}. Yıl Dönümünüz Kutlu Olsun {first_name} {last_name}!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{years}. Yıl Dönümü</title>
        <style>
            @media (prefers-color-scheme: dark) {{
                .email-container {{
                    background-color: #1a1a1a !important;
                }}
                .card-background {{
                    background-color: #2d2d2d !important;
                    border-color: #404040 !important;
                }}
            }}
            
            body {{
                margin: 0;
                padding: 20px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                border: 1px solid #e0e0e0;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px 20px 20px 20px;
                text-align: right;
                position: relative;
                overflow: hidden;
            }}
            
            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><polygon points="50,10 60,40 90,40 70,60 80,90 50,75 20,90 30,60 10,40 40,40" fill="rgba(255,255,255,0.2)"/></svg>');
                animation: sparkle 15s infinite linear;
            }}
            
            @keyframes sparkle {{
                0% {{ transform: rotate(0deg) scale(1); }}
                50% {{ transform: rotate(180deg) scale(1.1); }}
                100% {{ transform: rotate(360deg) scale(1); }}
            }}
            
            .logo {{
                color: white;
                font-size: 1.8rem;
                font-weight: 300;
                position: relative;
                z-index: 2;
                margin-bottom: 10px;
            }}
            
            .logo .plus {{
                font-weight: 700;
            }}
            
            .main-content {{
                padding: 40px 30px;
                background: #ffffff;
                text-align: center;
            }}
            
            .title {{
                font-size: 3rem;
                color: #667eea;
                margin: 20px 0;
                font-weight: 300;
                letter-spacing: 1px;
            }}
            
            .years-badge {{
                background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                color: white;
                padding: 15px 30px;
                border-radius: 50px;
                display: inline-block;
                margin: 20px 0;
                font-size: 2rem;
                font-weight: 700;
                box-shadow: 0 8px 20px rgba(255, 215, 0, 0.4);
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .name {{
                font-size: 1.8rem;
                color: #333;
                margin: 30px 0;
                font-weight: 500;
            }}
            
            .message {{
                font-size: 1.2rem;
                line-height: 1.8;
                color: #555;
                margin: 30px 0;
                font-weight: 400;
            }}
            
            .achievement-section {{
                margin: 40px 0;
                position: relative;
            }}
            
            .trophy {{
                font-size: 6rem;
                margin: 20px 0;
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
                animation: glow 2s ease-in-out infinite alternate;
            }}
            
            @keyframes glow {{
                from {{ filter: drop-shadow(0 4px 8px rgba(255, 215, 0, 0.3)); }}
                to {{ filter: drop-shadow(0 4px 15px rgba(255, 215, 0, 0.6)); }}
            }}
            
            .celebration-text {{
                font-size: 1.8rem;
                color: #667eea;
                font-weight: 600;
                margin: 20px 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            }}
            
            .wishes {{
                background: linear-gradient(135deg, #E8F0FF 0%, #F0F4FF 100%);
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
                border-left: 5px solid #667eea;
            }}
            
            .footer {{
                background: #f8f9fa;
                padding: 30px;
                text-align: center;
                color: #666;
                border-top: 1px solid #e0e0e0;
            }}
            
            .company-name {{
                color: #667eea;
                font-weight: 600;
                font-size: 1.1rem;
            }}
            
            /* Dark mode adjustments */
            @media (prefers-color-scheme: dark) {{
                .main-content {{
                    background-color: #2d2d2d !important;
                    color: #e0e0e0 !important;
                }}
                .name {{
                    color: #e0e0e0 !important;
                }}
                .message {{
                    color: #c0c0c0 !important;
                }}
                .wishes {{
                    background: linear-gradient(135deg, #1a1a3a 0%, #2a2a4a 100%) !important;
                    color: #e0e0e0 !important;
                }}
                .footer {{
                    background-color: #1a1a1a !important;
                    color: #a0a0a0 !important;
                    border-top-color: #404040 !important;
                }}
            }}
            
            /* Mobile responsiveness */
            @media (max-width: 600px) {{
                .email-container {{
                    margin: 10px;
                    border-radius: 15px;
                }}
                .title {{
                    font-size: 2.2rem;
                }}
                .trophy {{
                    font-size: 4rem;
                }}
                .main-content {{
                    padding: 30px 20px;
                }}
                .years-badge {{
                    font-size: 1.5rem;
                    padding: 12px 25px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">
                    <span class="plus">plus</span> Kitchen
                </div>
            </div>
            
            <div class="main-content">
                <div class="title">İş Yıl Dönümü Kutlaması</div>
                
                <div class="years-badge">{years} YIL</div>
                
                <div class="name">{title} {first_name} {last_name}</div>
                
                <div class="wishes">
                    <div class="message">
                        Plus Kitchen ailesindeki {years}. yılınızı kutluyoruz!<br><br>
                        Gösterdiğiniz özveri, başarılarınız ve<br>
                        değerli katkılarınız için teşekkür ederiz.<br><br>
                        Sizinle çalışmak bizim için büyük bir onur.
                    </div>
                </div>
                
                <div class="achievement-section">
                    <div class="trophy">🏆</div>
                    <div class="celebration-text">Nice yıllar birlikte!</div>
                </div>
                
                <div style="background: linear-gradient(135deg, #FFE082 0%, #FFB74D 100%); padding: 20px; border-radius: 15px; margin: 20px 0;">
                    <div style="color: #333; font-weight: 600; margin-bottom: 10px;">🎁 Size Özel Hediyeniz</div>
                    <div style="color: #555; font-size: 0.95rem;">İnsan Kaynakları departmanımızda sizleri bekliyor!</div>
                </div>
            </div>
            
            <div class="footer">
                <div class="company-name">Plus Kitchen Yönetimi</div>
                <div style="margin-top: 10px; font-size: 0.9rem;">
                    portal.pluskitchen.com.tr
                </div>
                <div style="margin-top: 15px; font-size: 0.8rem; opacity: 0.7;">
                    Bu otomatik bir e-postadır. Plus Kitchen Portal sistemi tarafından gönderilmiştir.
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        success = email_service.send_email(to_email, subject, html_content)
        if success:
            print(f"🏆 Modern iş yıl dönümü e-postası başarıyla gönderildi: {to_email}")
        else:
            print(f"❌ Modern iş yıl dönümü e-postası gönderilemedi: {to_email}")
        return success
    except Exception as e:
        print(f"❌ E-posta gönderme hatası: {e}")
        return False

def main():
    """Ana fonksiyon - Modern tasarımlı test e-postaları gönder"""
    print("🎨 Modern tasarımlı e-postalar gönderiliyor...")
    print("=" * 60)
    
    # Test edilecek kişiler
    recipients = [
        {"email": "ali.kok@pluskitchen.com.tr", "first_name": "Ali", "last_name": "Kök", "years": 5, "title": "Sn."},
        {"email": "yeliz.ay@pluskitchen.com.tr", "first_name": "Yeliz", "last_name": "Ay", "years": 3, "title": "Sn."}
    ]
    
    total_success = 0
    total_emails = 0
    
    for person in recipients:
        print(f"\n🎨 {person['first_name']} {person['last_name']} için modern e-postalar...")
        print("-" * 40)
        
        # Doğum günü e-postası
        print("🎂 Modern doğum günü e-postası gönderiliyor...")
        birthday_success = send_modern_birthday_email(
            person['email'], person['first_name'], person['last_name'], person['title']
        )
        total_emails += 1
        if birthday_success:
            total_success += 1
        
        # İş yıl dönümü e-postası
        print("🏆 Modern iş yıl dönümü e-postası gönderiliyor...")
        anniversary_success = send_modern_anniversary_email(
            person['email'], person['first_name'], person['last_name'], person['years'], person['title']
        )
        total_emails += 1
        if anniversary_success:
            total_success += 1
        
        print(f"✅ {person['first_name']} için sonuç: {('✅' if birthday_success else '❌')} Doğum günü, {('✅' if anniversary_success else '❌')} Yıl dönümü")
    
    # Genel sonuç raporu
    print("\n" + "=" * 60)
    print("🎨 MODERN TASARIM SONUÇ RAPORU:")
    print(f"📊 Toplam gönderilen e-posta: {total_success}/{total_emails}")
    print(f"📈 Başarı oranı: {(total_success/total_emails)*100:.1f}%")
    
    if total_success == total_emails:
        print("\n🎉 Tüm modern tasarımlı e-postalar başarıyla gönderildi!")
        print("📧 E-posta kutularını kontrol edebilirsiniz.")
        print("🎨 Dark/Light mode uyumlu tasarım aktif!")
        print("✨ Ekteki tasarımla uyumlu modern görünüm!")
    else:
        print("\n⚠️ Bazı e-postalar gönderilemedi. SMTP ayarlarını kontrol edin.")

if __name__ == '__main__':
    main()