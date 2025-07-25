#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import pymysql
from werkzeug.security import generate_password_hash
import re
from datetime import datetime
import os

def get_db_connection():
    """Database connection with fallback passwords"""
    MYSQL_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'database': 'corporate_communicator',
        'charset': 'utf8mb4',
        'port': 3306
    }
    
    passwords_to_try = ['255223', '255223Rtv', '', 'root', 'admin', '123456', '2552232']
    
    for password in passwords_to_try:
        try:
            config = MYSQL_CONFIG.copy()
            config['password'] = password
            config['cursorclass'] = pymysql.cursors.DictCursor
            print(f"🔄 Trying password: {'[empty]' if password == '' else '[hidden]'}")
            connection = pymysql.connect(**config)
            print(f"✅ Database connected successfully!")
            return connection
        except pymysql.err.OperationalError as e:
            if "Access denied" in str(e):
                continue
            else:
                print(f"❌ Database connection error: {e}")
                raise e
    
    # If all passwords fail, try without password
    try:
        config = MYSQL_CONFIG.copy()
        config['cursorclass'] = pymysql.cursors.DictCursor
        print("🔄 Trying without password...")
        connection = pymysql.connect(**config)
        print("✅ Database connected without password!")
        return connection
    except Exception as e:
        print(f"❌ Final attempt failed: {e}")
        return None

def clean_turkish_chars(text):
    """Türkçe karakterleri temizle"""
    if not text:
        return ""
    
    # Türkçe karakter dönüşümleri
    replacements = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G', 
        'ı': 'i', 'I': 'I',
        'İ': 'I', 'i': 'i',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    
    for tr_char, en_char in replacements.items():
        text = text.replace(tr_char, en_char)
    
    # Boşlukları kaldır ve küçük harfe çevir
    text = re.sub(r'[^a-zA-Z0-9]', '', text).lower()
    
    return text

def generate_password_from_user(first_name, birth_date):
    """Kullanıcı adından şifre üret: isim + doğum yılı"""
    try:
        # İsmi temizle
        clean_name = clean_turkish_chars(first_name)
        
        # Doğum yılını al
        if isinstance(birth_date, str):
            # String formatında ise parse et
            birth_year = datetime.strptime(birth_date, '%Y-%m-%d').year
        else:
            # Datetime objesi ise direkt al
            birth_year = birth_date.year
        
        # Şifre: temizlenmiş_isim + doğum_yılı
        password = f"{clean_name}{birth_year}"
        
        return password
    
    except Exception as e:
        print(f"❌ Password generation error for {first_name}: {e}")
        return f"plus{datetime.now().year}"

def main():
    """Ana fonksiyon"""
    print("🔄 Şifre üretimi ve Excel çıktısı başlatılıyor...")
    
    try:
        # Database bağlantısı
        conn = get_db_connection()
        if not conn:
            print("❌ Database bağlantısı başarısız!")
            return
        
        cursor = conn.cursor()
        
        # Kullanıcıları ve departman bilgilerini getir (admin hariç)
        query = """
        SELECT 
            u.id,
            u.username,
            u.first_name,
            u.last_name,
            u.email,
            u.birth_date,
            u.department_id,
            d.name as department_name
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE u.username != 'admin'
        ORDER BY d.name, u.first_name, u.last_name
        """
        
        cursor.execute(query)
        users = cursor.fetchall()
        
        print(f"📊 {len(users)} kullanıcı bulundu")
        
        # Şifreleri üret ve güncelle
        updated_users = []
        
        for user in users:
            try:
                # Yeni şifre üret
                new_password = generate_password_from_user(user['first_name'], user['birth_date'])
                hashed_password = generate_password_hash(new_password)
                
                # Database'de güncelle
                cursor.execute(
                    "UPDATE users SET password = %s WHERE id = %s",
                    (hashed_password, user['id'])
                )
                
                # Excel için kaydet
                user_data = {
                    'ID': user['id'],
                    'Kullanıcı Adı': user['username'],
                    'Ad': user['first_name'],
                    'Soyad': user['last_name'],
                    'Departman': user['department_name'] if user['department_name'] else 'Bilinmiyor',
                    'E-posta': user['email'],
                    'Doğum Tarihi': user['birth_date'].strftime('%d/%m/%Y') if user['birth_date'] else '',
                    'Yeni Şifre': new_password
                }
                
                updated_users.append(user_data)
                print(f"✅ {user['first_name']} {user['last_name']} - Şifre: {new_password}")
                
            except Exception as e:
                print(f"❌ {user['first_name']} {user['last_name']} için hata: {e}")
        
        # Değişiklikleri kaydet
        conn.commit()
        print(f"💾 {len(updated_users)} kullanıcının şifresi güncellendi")
        
        # Excel dosyası oluştur
        df = pd.DataFrame(updated_users)
        
        # Dosya adı
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"kullanici_sifreler_departmanlar_{timestamp}.xlsx"
        
        # Excel'e yaz
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Kullanıcı Şifreleri', index=False)
            
            # Worksheet'i al ve formatla
            worksheet = writer.sheets['Kullanıcı Şifreleri']
            
            # Sütun genişliklerini ayarla
            column_widths = {
                'A': 8,   # ID
                'B': 20,  # Kullanıcı Adı
                'C': 15,  # Ad
                'D': 15,  # Soyad
                'E': 25,  # Departman
                'F': 30,  # E-posta
                'G': 15,  # Doğum Tarihi
                'H': 15   # Yeni Şifre
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
        
        print(f"📄 Excel dosyası oluşturuldu: {filename}")
        
        # Özet bilgi
        print("\n📋 ÖZET:")
        print(f"• Toplam kullanıcı: {len(updated_users)}")
        print(f"• Excel dosyası: {filename}")
        print(f"• Dosya boyutu: {os.path.getsize(filename) / 1024:.1f} KB")
        
        # Departman bazında dağılım
        dept_counts = df['Departman'].value_counts()
        print("\n🏢 Departman Dağılımı:")
        for dept, count in dept_counts.items():
            print(f"  • {dept}: {count} kişi")
        
        conn.close()
        print("\n✅ İşlem tamamlandı!")
        
    except Exception as e:
        print(f"❌ Genel hata: {e}")

if __name__ == "__main__":
    main() 