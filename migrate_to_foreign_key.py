import pymysql

# Database connection
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '255223Rtv',
    'database': 'corporate_communicator',
    'charset': 'utf8mb4'
}

def migrate_to_foreign_key():
    """
    Users tablosuna department_id ekleyip foreign key relationship kurar
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print("🚀 Migration başlıyor: Users -> Departments Foreign Key")
        
        # 1. Backup mevcut data
        print("\n1️⃣ Backup alınıyor...")
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE department IS NOT NULL")
        user_count = cursor.fetchone()['count']
        print(f"   📊 {user_count} kullanıcının departman bilgisi backup alınacak")
        
        # 2. department_id column'u ekle (eğer yoksa)
        print("\n2️⃣ department_id column'u ekleniyor...")
        try:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN department_id INT NULL 
                AFTER department
            """)
            print("   ✅ department_id column'u eklendi")
        except pymysql.err.OperationalError as e:
            if "Duplicate column name" in str(e):
                print("   ⚠️ department_id column'u zaten mevcut")
            else:
                raise e
        
        # 3. department_id'leri güncelle
        print("\n3️⃣ department_id'ler güncelleniyor...")
        cursor.execute("""
            UPDATE users u 
            INNER JOIN departments d ON u.department = d.name 
            SET u.department_id = d.id 
            WHERE u.department IS NOT NULL
        """)
        updated_count = cursor.rowcount
        print(f"   ✅ {updated_count} kullanıcının department_id'si güncellendi")
        
        # 4. Foreign key constraint ekle
        print("\n4️⃣ Foreign key constraint ekleniyor...")
        try:
            cursor.execute("""
                ALTER TABLE users 
                ADD CONSTRAINT fk_users_department 
                FOREIGN KEY (department_id) REFERENCES departments(id) 
                ON DELETE SET NULL ON UPDATE CASCADE
            """)
            print("   ✅ Foreign key constraint eklendi")
        except pymysql.err.OperationalError as e:
            if "Duplicate key name" in str(e):
                print("   ⚠️ Foreign key constraint zaten mevcut")
            else:
                raise e
        
        # 5. Doğrulama
        print("\n5️⃣ Doğrulama yapılıyor...")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(u.department_id) as users_with_dept_id,
                COUNT(u.department) as users_with_dept_name
            FROM users u
        """)
        validation = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(*) as unmatched_count
            FROM users u
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE u.department_id IS NOT NULL AND d.id IS NULL
        """)
        unmatched = cursor.fetchone()['unmatched_count']
        
        print(f"   📊 Toplam kullanıcı: {validation['total_users']}")
        print(f"   📊 department_id olan: {validation['users_with_dept_id']}")
        print(f"   📊 department name olan: {validation['users_with_dept_name']}")
        print(f"   📊 Eşleşmeyen FK: {unmatched}")
        
        if unmatched == 0:
            print("   ✅ Tüm foreign key'ler geçerli!")
        else:
            print("   ❌ Bazı foreign key'ler geçersiz!")
            
        # Değişiklikleri kaydet
        conn.commit()
        print("\n🎉 Migration tamamlandı!")
        print("\n📝 Sonraki adımlar:")
        print("   1. app.py'deki query'leri department_id kullanacak şekilde güncelleyin")
        print("   2. Test edin")
        print("   3. İsterseniz department column'unu silebilirsiniz (backward compatibility için önerilmez)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

def rollback_migration():
    """
    Migration'ı geri alır (foreign key ve department_id'yi siler)
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        
        print("🔄 Migration geri alınıyor...")
        
        # Foreign key constraint sil
        try:
            cursor.execute("ALTER TABLE users DROP FOREIGN KEY fk_users_department")
            print("   ✅ Foreign key constraint silindi")
        except:
            print("   ⚠️ Foreign key constraint zaten yok")
        
        # department_id column sil
        try:
            cursor.execute("ALTER TABLE users DROP COLUMN department_id")
            print("   ✅ department_id column'u silindi")
        except:
            print("   ⚠️ department_id column'u zaten yok")
            
        conn.commit()
        print("✅ Rollback tamamlandı!")
        conn.close()
        
    except Exception as e:
        print(f"❌ Rollback Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        migrate_to_foreign_key() 