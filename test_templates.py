#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Email Template Test Scripti
"""

from enhanced_email_service import enhanced_email_service
from datetime import datetime, date

def test_birthday_email():
    """Doğum günü email template'ini test et"""
    print("🎂 Doğum günü email template'i test ediliyor...")
    
    test_email = "ali.kok@pluskitchen.com.tr"
    first_name = "Ali"
    last_name = "KÖK"
    birth_date = date(1990, 7, 28)  # Örnek doğum tarihi
    
    try:
        success = enhanced_email_service.send_birthday_email(
            to_email=test_email,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date
        )
        
        if success:
            print("✅ Doğum günü email template'i başarıyla gönderildi!")
            return True
        else:
            print("❌ Doğum günü email template'i gönderilemedi")
            return False
    except Exception as e:
        print(f"❌ Doğum günü email hatası: {e}")
        return False

def test_anniversary_email():
    """İş yıl dönümü email template'ini test et"""
    print("\n🏆 İş yıl dönümü email template'i test ediliyor...")
    
    test_email = "ali.kok@pluskitchen.com.tr"
    first_name = "Ali"
    last_name = "Koçak"
    hire_date = date(2020, 7, 28)  # 4 yıl önce işe başlamış
    years = 4
    
    try:
        success = enhanced_email_service.send_anniversary_email(
            to_email=test_email,
            first_name=first_name,
            last_name=last_name,
            hire_date=hire_date,
            years=years
        )
        
        if success:
            print("✅ İş yıl dönümü email template'i başarıyla gönderildi!")
            return True
        else:
            print("❌ İş yıl dönümü email template'i gönderilemedi")
            return False
    except Exception as e:
        print(f"❌ İş yıl dönümü email hatası: {e}")
        return False

def test_password_reset_email():
    """Şifre sıfırlama email'ini test et"""
    print("\n🔐 Şifre sıfırlama email'i test ediliyor...")
    
    test_email = "ali.kok@pluskitchen.com.tr"
    reset_link = "http://portal.pluskitchen.com.tr/reset-password/test-token-456"
    user_name = "Ali Koçak"
    
    try:
        success = enhanced_email_service.send_password_reset_email(
            to_email=test_email,
            reset_link=reset_link,
            user_name=user_name
        )
        
        if success:
            print("✅ Şifre sıfırlama email'i başarıyla gönderildi!")
            return True
        else:
            print("❌ Şifre sıfırlama email'i gönderilemedi")
            return False
    except Exception as e:
        print(f"❌ Şifre sıfırlama email hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("=" * 70)
    print("🎨 PLUS KITCHEN PORTAL - HTML EMAIL TEMPLATE TESTİ")
    print("=" * 70)
    print(f"📅 Test Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("=" * 70)
    
    # Email servis bilgileri
    print("\n📧 Email Servis Konfigürasyonu:")
    print(f"   SMTP Sunucu: {enhanced_email_service.smtp_server}")
    print(f"   SMTP Port: {enhanced_email_service.smtp_port}")
    print(f"   Kullanıcı: {enhanced_email_service.smtp_username}")
    print(f"   Template Dizini: {enhanced_email_service.template_dir}")
    
    # Test sonuçları
    test_results = []
    
    # Test 1: Doğum günü email
    print("\n" + "="*50)
    print("TEST 1: DOĞUM GÜNÜ EMAIL TEMPLATE")
    print("="*50)
    result1 = test_birthday_email()
    test_results.append(("Doğum Günü Template", result1))
    
    # Test 2: İş yıl dönümü email
    print("\n" + "="*50)
    print("TEST 2: İŞ YIL DÖNÜMÜ EMAIL TEMPLATE")
    print("="*50)
    result2 = test_anniversary_email()
    test_results.append(("İş Yıl Dönümü Template", result2))
    
    # Test 3: Şifre sıfırlama email
    print("\n" + "="*50)
    print("TEST 3: ŞİFRE SIFIRLAMA EMAIL")
    print("="*50)
    result3 = test_password_reset_email()
    test_results.append(("Şifre Sıfırlama", result3))
    
    # Sonuçlar özeti
    print("\n" + "="*70)
    print("📊 TEST SONUÇLARI ÖZETİ")
    print("="*70)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name:25} : {status}")
        if not result:
            all_passed = False
    
    print("="*70)
    if all_passed:
        print("🎉 TÜM TEMPLATE TESTLER BAŞARILI!")
        print("📧 HTML email template'leri çalışıyor.")
        print("🎨 Profesyonel kutlama mailleri hazır!")
    else:
        print("⚠️ Bazı template testler başarısız.")
        print("📁 Template dosyalarını kontrol edin.")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Test sırasında beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
