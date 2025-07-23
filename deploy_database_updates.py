import pymysql

# UZAK SUNUCU İÇİN Database connection
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '255223Rtv',  # UZAK SUNUCU ŞİFRESİ
    'database': 'corporate_communicator',
    'charset': 'utf8mb4'
}

def deploy_database_updates():
    """
    Uzak sunucu için tüm database güncellemelerini yapar
    - Toplantı odası tabloları
    - Terfi duyuları tablosu  
    - Users tablosu güncelleme
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        
        print("🚀 UZAK SUNUCU DATABASE GÜNCELLEMELERİ")
        print("=" * 50)
        
        # 1. Meeting rooms tablosu
        print("📋 1. Meeting rooms tablosu oluşturuluyor...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meeting_rooms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                capacity INT DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ meeting_rooms tablosu oluşturuldu")
        
        # 2. Room reservations tablosu
        print("📋 2. Room reservations tablosu oluşturuluyor...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS room_reservations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_id INT NOT NULL,
                user_id INT NOT NULL,
                reservation_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                purpose TEXT,
                status ENUM('pending', 'approved', 'cancelled') DEFAULT 'approved',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES meeting_rooms(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                INDEX idx_date_room (reservation_date, room_id),
                INDEX idx_user (user_id)
            )
        """)
        print("✅ room_reservations tablosu oluşturuldu")
        
        # 3. Promotions tablosu
        print("📋 3. Promotions tablosu oluşturuluyor...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS promotions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                old_position VARCHAR(255),
                new_position VARCHAR(255) NOT NULL,
                department VARCHAR(255),
                promotion_date DATE NOT NULL,
                announcement_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                INDEX idx_promotion_date (promotion_date)
            )
        """)
        print("✅ promotions tablosu oluşturuldu")
        
        # 4. Users tablosuna can_reserve_rooms kolonu ekle
        print("📋 4. Users tablosu güncelleniyor...")
        
        # Kolon var mı kontrol et
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE table_name = 'users' 
            AND column_name = 'can_reserve_rooms' 
            AND table_schema = 'corporate_communicator'
        """)
        
        column_exists = cursor.fetchone()[0]
        
        if column_exists == 0:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN can_reserve_rooms BOOLEAN DEFAULT FALSE
            """)
            print("✅ can_reserve_rooms kolonu eklendi")
        else:
            print("ℹ️  can_reserve_rooms kolonu zaten mevcut")
        
        # 5. Admin kullanıcılara otomatik toplantı odası izni ver
        print("📋 5. Admin kullanıcılara toplantı odası izni veriliyor...")
        cursor.execute("""
            UPDATE users 
            SET can_reserve_rooms = TRUE 
            WHERE role_id IN (
                SELECT id FROM roles WHERE name IN ('Admin', 'İK Yöneticisi', 'İçerik Yöneticisi')
            )
        """)
        updated_count = cursor.rowcount
        print(f"✅ {updated_count} admin kullanıcıya toplantı odası izni verildi")
        
        # 6. Varsayılan toplantı odalarını ekle
        print("📋 6. Varsayılan toplantı odaları ekleniyor...")
        cursor.execute("SELECT COUNT(*) FROM meeting_rooms")
        room_count = cursor.fetchone()[0]
        
        if room_count == 0:
            cursor.execute("""
                INSERT INTO meeting_rooms (name, description, capacity) VALUES
                ('Büyük Toplantı Odası', 'Ana toplantı odası, projektör ve video konferans imkanı', 12),
                ('Think Tank', 'Küçük toplantı odası, yaratıcı çalışmalar için ideal', 6)
            """)
            print("✅ Varsayılan toplantı odaları eklendi")
        else:
            print("ℹ️  Toplantı odaları zaten mevcut")
        
        # 7. Örnek terfi duyuruları ekle (isteğe bağlı)
        print("📋 7. Örnek terfi duyuruları kontrol ediliyor...")
        cursor.execute("SELECT COUNT(*) FROM promotions")
        promotion_count = cursor.fetchone()[0]
        
        if promotion_count == 0:
            print("ℹ️  Henüz terfi duyurusu yok (normal)")
        else:
            print(f"ℹ️  {promotion_count} terfi duyurusu mevcut")
        
        conn.commit()
        print("\n🎉 TÜM DATABASE GÜNCELLEMELERİ BAŞARILI!")
        print("=" * 50)
        print("📝 YAPILAN DEĞİŞİKLİKLER:")
        print("   ✓ Toplantı odası rezervasyon sistemi")
        print("   ✓ Terfi duyuları sistemi")
        print("   ✓ Kullanıcı yetkilendirme sistemi")
        print("   ✓ Admin kullanıcılara otomatik izinler")
        print("   ✓ 2 adet varsayılan toplantı odası")
        print("\n💡 Artık uygulama güncellemelerini deploy edebilirsiniz!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ HATA OLUŞTU: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        print("\n🔧 HATA GİDERME ÖNERİLERİ:")
        print("   - Database bağlantı bilgilerini kontrol edin")
        print("   - MySQL servisi çalışıyor mu kontrol edin")
        print("   - Yetki problemi varsa root kullanıcısını kontrol edin")

def check_database_status():
    """
    Database durumunu kontrol eder
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        
        print("🔍 DATABASE DURUM KONTROLÜ")
        print("=" * 30)
        
        # Tabloları kontrol et
        tables_to_check = ['meeting_rooms', 'room_reservations', 'promotions']
        
        for table in tables_to_check:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'corporate_communicator' 
                AND table_name = '{table}'
            """)
            exists = cursor.fetchone()[0]
            status = "✅ Mevcut" if exists else "❌ Eksik"
            print(f"   {table}: {status}")
        
        # can_reserve_rooms kolonu kontrol et
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE table_name = 'users' 
            AND column_name = 'can_reserve_rooms' 
            AND table_schema = 'corporate_communicator'
        """)
        column_exists = cursor.fetchone()[0]
        status = "✅ Mevcut" if column_exists else "❌ Eksik"
        print(f"   users.can_reserve_rooms: {status}")
        
        conn.close()
        print("\n" + "=" * 30)
        
    except Exception as e:
        print(f"❌ Database bağlantı hatası: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_database_status()
    else:
        print("⚠️  UZAK SUNUCU DEPLOYMENT SCRIPTI")
        print("Bu script uzak sunucuda çalıştırılmak üzere hazırlanmıştır.")
        print("Şifre: 255223Rtv kullanılıyor\n")
        
        confirm = input("Devam etmek istiyor musunuz? (evet/hayır): ")
        if confirm.lower() in ['evet', 'e', 'yes', 'y']:
            deploy_database_updates()
        else:
            print("❌ İşlem iptal edildi.")
            
        print(f"\n💡 Database durumunu kontrol etmek için: python {__file__} check") 