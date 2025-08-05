#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

try:
    from email_service import email_service
    from app import get_db_connection
    print("✅ Email service imported successfully")
except ImportError as e:
    print(f"❌ Failed to import email service: {e}")
    sys.exit(1)

def get_base_email_style():
    """Tüm e-postalar için temel CSS stileri"""
    return """
    <style>
        @media (prefers-color-scheme: dark) {
            .email-container {
                background-color: #1a1a1a !important;
            }
            .main-content {
                background-color: #2d2d2d !important;
                color: #e0e0e0 !important;
            }
            .name, .message, .title {
                color: #e0e0e0 !important;
            }
            .wishes {
                background: linear-gradient(135deg, #1a3a1a 0%, #2a4a2a 100%) !important;
                color: #e0e0e0 !important;
            }
            .footer {
                background-color: #1a1a1a !important;
                color: #a0a0a0 !important;
                border-top-color: #404040 !important;
            }
        }
        
        body {
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .logo {
            color: white;
            font-size: 1.8rem;
            font-weight: 300;
            position: relative;
            z-index: 2;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .logo .plus {
            font-weight: 700;
        }
        
        .main-content {
            padding: 40px 30px;
            background: #ffffff;
            text-align: center;
            position: relative;
        }
        
        .footer {
            background: rgba(0,0,0,0.05);
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 1px solid rgba(0,0,0,0.1);
        }
        
        .company-name {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .decorative-elements {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
        }
        
        .floating-element {
            position: absolute;
            animation: float 6s ease-in-out infinite;
            opacity: 0.6;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        /* Mobile responsiveness */
        @media (max-width: 600px) {
            .email-container {
                margin: 10px;
                border-radius: 15px;
            }
            .main-content {
                padding: 30px 20px;
            }
        }
    </style>
    """

def send_birthday_email(to_email, first_name, last_name, title="Sn."):
    """Modern doğum günü e-postası"""
    
    subject = f"🎉 Mutlu Yıllar {first_name} {last_name}!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mutlu Yıllar</title>
        {get_base_email_style()}
        <style>
            body {{
                background: linear-gradient(135deg, #4CAF50 0%, #81C784 25%, #A5D6A7 50%, #C8E6C9 75%, #E8F5E8 100%);
            }}
            
            .header {{
                background: linear-gradient(135deg, #2E7D32 0%, #388E3C 50%, #4CAF50 100%);
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
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="25" cy="25" r="3" fill="rgba(255,255,255,0.2)"/><circle cx="75" cy="50" r="2" fill="rgba(255,255,255,0.15)"/></svg>');
                animation: sparkle 20s infinite linear;
            }}
            
            @keyframes sparkle {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            .title {{
                font-size: 3.5rem;
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
                color: #2E7D32;
                margin: 30px 0;
                font-weight: 600;
            }}
            
            .cake {{
                font-size: 6rem;
                margin: 20px 0;
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
                animation: bounce 2s ease-in-out infinite;
            }}
            
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0px); }}
                50% {{ transform: translateY(-10px); }}
            }}
            
            .wishes {{
                background: linear-gradient(135deg, #E8F5E8 0%, #F1F8E9 100%);
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
                border-left: 5px solid #4CAF50;
                box-shadow: 0 5px 15px rgba(76, 175, 80, 0.2);
            }}
            
            .message {{
                font-size: 1.2rem;
                line-height: 1.8;
                color: #2E7D32;
                margin: 20px 0;
                font-weight: 500;
            }}
            
            .company-name {{
                color: #4CAF50;
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
                    <div class="floating-element" style="top: 10%; left: 5%; animation-delay: 0s;">🌿</div>
                    <div class="floating-element" style="top: 20%; right: 8%; animation-delay: 1s;">🍃</div>
                    <div class="floating-element" style="bottom: 15%; left: 10%; animation-delay: 2s;">🌱</div>
                    <div class="floating-element" style="bottom: 25%; right: 5%; animation-delay: 0.5s;">🌿</div>
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
                
                <div class="cake">🎂</div>
                <div style="font-size: 2rem; color: #4CAF50; font-weight: 600; margin: 20px 0;">İyi ki doğdunuz.</div>
            </div>
            
            <div class="footer">
                <div class="company-name">Plus Kitchen İnsan Kaynakları</div>
                <div style="margin-top: 10px; font-size: 0.9rem;">portal.pluskitchen.com.tr</div>
                <div style="margin-top: 15px; font-size: 0.8rem; opacity: 0.7;">
                    Bu otomatik bir e-postadır. Plus Kitchen Portal sistemi tarafından gönderilmiştir.
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return email_service.send_email(to_email, subject, html_content)

def send_anniversary_email(to_email, first_name, last_name, years, title="Sn."):
    """Modern iş yıl dönümü e-postası"""
    
    subject = f"🏆 {years}. Yıl Dönümünüz Kutlu Olsun!"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{years}. Yıl Dönümü</title>
        {get_base_email_style()}
        <style>
            body {{
                background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 25%, #45B7D1 50%, #96CEB4 75%, #FFEAA7 100%);
            }}
            
            .header {{
                background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 50%, #45B7D1 100%);
                padding: 30px 20px 20px 20px;
                text-align: right;
                position: relative;
                overflow: hidden;
            }}
            
            .title {{
                font-size: 3rem;
                color: #FF6B6B;
                margin: 20px 0;
                font-weight: 600;
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
                color: #4ECDC4;
                margin: 30px 0;
                font-weight: 600;
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
            
            .wishes {{
                background: linear-gradient(135deg, #E8F4FD 0%, #F0F8FF 100%);
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
                border-left: 5px solid #4ECDC4;
                box-shadow: 0 5px 15px rgba(78, 205, 196, 0.2);
            }}
            
            .message {{
                font-size: 1.2rem;
                line-height: 1.8;
                color: #2C3E50;
                margin: 20px 0;
                font-weight: 500;
            }}
            
            .company-name {{
                color: #4ECDC4;
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
                
                <div class="trophy">🏆</div>
                <div style="font-size: 1.8rem; color: #4ECDC4; font-weight: 600; margin: 20px 0;">
                    Nice yıllar birlikte!
                </div>
                
                <div style="background: linear-gradient(135deg, #FFE082 0%, #FFB74D 100%); padding: 20px; border-radius: 15px; margin: 20px 0; box-shadow: 0 5px 15px rgba(255, 183, 77, 0.3);">
                    <div style="color: #333; font-weight: 600; margin-bottom: 10px;">🎁 Size Özel Hediyeniz</div>
                    <div style="color: #555; font-size: 0.95rem;">İnsan Kaynakları departmanımızda sizleri bekliyor!</div>
                </div>
            </div>
            
            <div class="footer">
                <div class="company-name">Plus Kitchen Yönetimi</div>
                <div style="margin-top: 10px; font-size: 0.9rem;">portal.pluskitchen.com.tr</div>
                <div style="margin-top: 15px; font-size: 0.8rem; opacity: 0.7;">
                    Bu otomatik bir e-postadır. Plus Kitchen Portal sistemi tarafından gönderilmiştir.
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return email_service.send_email(to_email, subject, html_content)

def send_promotion_email(to_email, first_name, last_name, new_position, title="Sn."):
    """Modern terfi e-postası"""
    
    subject = f"🎉 Tebrikler! Yeni Pozisyonunuz: {new_position}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Terfi Kutlaması</title>
        {get_base_email_style()}
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                padding: 30px 20px 20px 20px;
                text-align: right;
                position: relative;
                overflow: hidden;
            }}
            
            .title {{
                font-size: 3.2rem;
                color: #667eea;
                margin: 20px 0;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            
            .name {{
                font-size: 1.8rem;
                color: #764ba2;
                margin: 30px 0;
                font-weight: 600;
            }}
            
            .position-badge {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px 30px;
                border-radius: 15px;
                display: inline-block;
                margin: 20px 0;
                font-size: 1.3rem;
                font-weight: 600;
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            }}
            
            .celebration {{
                font-size: 5rem;
                margin: 20px 0;
                animation: rotate 3s ease-in-out infinite;
            }}
            
            @keyframes rotate {{
                0%, 100% {{ transform: rotate(-10deg); }}
                50% {{ transform: rotate(10deg); }}
            }}
            
            .wishes {{
                background: linear-gradient(135deg, #E8EAFF 0%, #F0F2FF 100%);
                padding: 25px;
                border-radius: 15px;
                margin: 30px 0;
                border-left: 5px solid #667eea;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
            }}
            
            .message {{
                font-size: 1.2rem;
                line-height: 1.8;
                color: #4A5568;
                margin: 20px 0;
                font-weight: 500;
            }}
            
            .company-name {{
                color: #667eea;
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
                <div class="title">TERFİ KUTLAMASI</div>
                
                <div class="celebration">🎊</div>
                
                <div class="name">{title} {first_name} {last_name}</div>
                
                <div class="position-badge">{new_position}</div>
                
                <div class="wishes">
                    <div class="message">
                        🎉 <strong>Tebrikler!</strong><br><br>
                        
                        Yeni pozisyonunuz için sizleri kutluyoruz!<br>
                        Bu terfiyi başarılı performansınız ve<br>
                        özverinizle hak ettiniz.<br><br>
                        
                        Yeni görevinizde de aynı başarıları<br>
                        göstereceğinize inanıyoruz.
                    </div>
                </div>
                
                <div style="background: linear-gradient(135deg, #98FB98 0%, #90EE90 100%); padding: 20px; border-radius: 15px; margin: 20px 0; box-shadow: 0 5px 15px rgba(152, 251, 152, 0.3);">
                    <div style="color: #2F4F2F; font-weight: 600; margin-bottom: 10px;">📋 Görev Detayları</div>
                    <div style="color: #556B2F; font-size: 0.95rem;">Yeni pozisyonunuz ile ilgili detaylar için İK departmanımızla görüşebilirsiniz.</div>
                </div>
            </div>
            
            <div class="footer">
                <div class="company-name">Plus Kitchen Yönetimi</div>
                <div style="margin-top: 10px; font-size: 0.9rem;">portal.pluskitchen.com.tr</div>
                <div style="margin-top: 15px; font-size: 0.8rem; opacity: 0.7;">
                    Bu otomatik bir e-postadır. Plus Kitchen Portal sistemi tarafından gönderilmiştir.
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return email_service.send_email(to_email, subject, html_content)

def send_department_birthday_reminder(department_id, birthday_person_name, birthday_date):
    """Departmana doğum günü hatırlatması gönder"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Departman yöneticilerini ve İK'yı bul
        cursor.execute("""
            SELECT DISTINCT u.email, u.first_name, u.last_name, d.name as dept_name
            FROM users u
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE (u.department_id = %s OR u.department_id = 1 OR u.is_admin = TRUE)
            AND u.email IS NOT NULL
            AND u.is_active = TRUE
        """, (department_id,))
        
        managers = cursor.fetchall()
        
        for manager in managers:
            subject = f"🎂 Departman Doğum Günü Hatırlatması - {birthday_person_name}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="tr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Doğum Günü Hatırlatması</title>
                {get_base_email_style()}
                <style>
                    body {{
                        background: linear-gradient(135deg, #FFB6C1 0%, #FFC0CB 25%, #FFE4E1 50%, #F0F8FF 75%, #E6E6FA 100%);
                    }}
                    
                    .header {{
                        background: linear-gradient(135deg, #FF69B4 0%, #FF1493 50%, #DC143C 100%);
                        padding: 30px 20px 20px 20px;
                        text-align: right;
                        position: relative;
                        overflow: hidden;
                    }}
                    
                    .title {{
                        font-size: 2.5rem;
                        color: #FF1493;
                        margin: 20px 0;
                        font-weight: 600;
                    }}
                    
                    .reminder-box {{
                        background: linear-gradient(135deg, #FFF0F5 0%, #FFE4E1 100%);
                        padding: 25px;
                        border-radius: 15px;
                        margin: 30px 0;
                        border-left: 5px solid #FF69B4;
                        box-shadow: 0 5px 15px rgba(255, 105, 180, 0.2);
                    }}
                    
                    .message {{
                        font-size: 1.1rem;
                        line-height: 1.6;
                        color: #8B008B;
                        margin: 15px 0;
                        font-weight: 500;
                    }}
                    
                    .company-name {{
                        color: #FF1493;
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
                        <div class="title">🎂 Doğum Günü Hatırlatması</div>
                        
                        <div style="font-size: 1.5rem; color: #FF1493; margin: 20px 0; font-weight: 600;">
                            Sevgili {manager[1]} {manager[2]},
                        </div>
                        
                        <div class="reminder-box">
                            <div class="message">
                                <strong>📅 BUGÜN DOĞUM GÜNÜ:</strong><br><br>
                                
                                👤 <strong>{birthday_person_name}</strong><br>
                                🏢 <strong>Departman:</strong> {manager[3] or 'Bilinmeyen'}<br>
                                🎂 <strong>Tarih:</strong> {birthday_date}<br><br>
                                
                                Lütfen departman olarak bu özel günü kutlamayı unutmayın! 🎉
                            </div>
                        </div>
                        
                        <div style="font-size: 4rem; margin: 20px 0;">🎈</div>
                        
                        <div style="background: linear-gradient(135deg, #FFE4B5 0%, #FFDAB9 100%); padding: 20px; border-radius: 15px; margin: 20px 0;">
                            <div style="color: #8B4513; font-weight: 600; margin-bottom: 10px;">💡 Öneriler</div>
                            <div style="color: #A0522D; font-size: 0.95rem;">
                                • Departman olarak küçük bir kutlama yapabilirsiniz<br>
                                • Pasta veya tatlı ikram edebilirsiniz<br>
                                • Güzel dileklerinizi iletebilirsiniz
                            </div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <div class="company-name">Plus Kitchen İnsan Kaynakları</div>
                        <div style="margin-top: 10px; font-size: 0.9rem;">portal.pluskitchen.com.tr</div>
                        <div style="margin-top: 15px; font-size: 0.8rem; opacity: 0.7;">
                            Bu otomatik bir hatırlatma e-postasıdır.
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            try:
                success = email_service.send_email(manager[0], subject, html_content)
                if success:
                    print(f"🎂 Departman hatırlatması gönderildi: {manager[0]}")
                else:
                    print(f"❌ Departman hatırlatması gönderilemedi: {manager[0]}")
            except Exception as e:
                print(f"❌ Hatırlatma gönderme hatası {manager[0]}: {e}")
                
    except Exception as e:
        print(f"❌ Departman hatırlatması hatası: {e}")
    finally:
        conn.close()

def send_test_emails():
    """Test e-postaları gönder"""
    print("🎨 Modern tasarımlı e-postalar gönderiliyor...")
    print("=" * 60)
    
    # Test edilecek kişiler
    recipients = [
        {"email": "ali.kok@pluskitchen.com.tr", "first_name": "Ali", "last_name": "Kök", "years": 5}
    ]
    
    for person in recipients:
        print(f"\n🎨 {person['first_name']} {person['last_name']} için e-postalar...")
        print("-" * 40)
        
        # Doğum günü e-postası
        print("🎂 Modern doğum günü e-postası...")
        send_birthday_email(person['email'], person['first_name'], person['last_name'])
        
        # İş yıl dönümü e-postası
        print("🏆 Modern iş yıl dönümü e-postası...")
        send_anniversary_email(person['email'], person['first_name'], person['last_name'], person['years'])
        
        # Terfi e-postası
        print("🎉 Modern terfi e-postası...")
        send_promotion_email(person['email'], person['first_name'], person['last_name'], "Kıdemli Uzman")
        
        # Departman hatırlatması
        print("📢 Departman doğum günü hatırlatması...")
        send_department_birthday_reminder(1, f"{person['first_name']} {person['last_name']}", "25 Ocak 2025")
    
    print("\n🎉 Tüm modern e-postalar gönderildi!")
    print("📧 Dark/Light mode uyumlu tasarım aktif!")

if __name__ == '__main__':
    send_test_emails()