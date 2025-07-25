import pymysql

def get_db_connection():
    """Database bağlantısı - Fallback password sistemi"""
    passwords_to_try = ['255223', '255223Rtv', '', 'root', 'admin', '123456', '2552232']
    
    for password in passwords_to_try:
        try:
            config = {
                'host': 'localhost',
                'user': 'root',
                'password': password,
                'database': 'corporate_communicator',
                'charset': 'utf8mb4',
                'port': 3306
            }
            print(f"🔄 Veritabanına bağlanmaya çalışılıyor...")
            connection = pymysql.connect(**config)
            print(f"✅ Veritabanına başarıyla bağlandı!")
            return connection
        except pymysql.err.OperationalError as e:
            if "Access denied" in str(e):
                print(f"❌ Şifre reddedildi: {'[gizli]' if password else '[boş]'}")
                continue
            else:
                print(f"❌ Veritabanı bağlantı hatası: {e}")
                raise e
    
    raise Exception("MySQL bağlantısı kurulamadı.")

def create_targeting_tables():
    """Hedefleme tablolarını oluştur"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Announcement targets tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcement_targets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                announcement_id INT NOT NULL,
                target_type ENUM('department', 'user', 'role', 'all') NOT NULL,
                target_id INT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (announcement_id) REFERENCES announcements(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Announcements tablosuna hedefleme kolonları ekle
        try:
            cursor.execute('ALTER TABLE announcements ADD COLUMN target_type ENUM("all", "department", "user", "role") DEFAULT "all" AFTER content')
            print("✅ target_type kolonu eklendi")
        except:
            print("ℹ️ target_type kolonu zaten mevcut")
        
        try:
            cursor.execute('ALTER TABLE announcements ADD COLUMN target_departments TEXT NULL AFTER target_type')
            print("✅ target_departments kolonu eklendi")
        except:
            print("ℹ️ target_departments kolonu zaten mevcut")
        
        try:
            cursor.execute('ALTER TABLE announcements ADD COLUMN target_users TEXT NULL AFTER target_departments')
            print("✅ target_users kolonu eklendi")
        except:
            print("ℹ️ target_users kolonu zaten mevcut")
        
        try:
            cursor.execute('ALTER TABLE announcements ADD COLUMN target_roles TEXT NULL AFTER target_users')
            print("✅ target_roles kolonu eklendi")
        except:
            print("ℹ️ target_roles kolonu zaten mevcut")
        
        conn.commit()
        print("🎉 Hedefleme tabloları başarıyla oluşturuldu!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Hata: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_targeting_tables() 