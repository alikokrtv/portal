import pymysql

# Database connection
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '255223Rtv',
    'database': 'corporate_communicator',
    'charset': 'utf8mb4'
}

def analyze_department_matching():
    """
    Department matching sorunlarını analiz eder
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print("🔍 Department Matching Analizi")
        print("=" * 50)
        
        # 1. NULL department_id'li kullanıcıları kontrol et
        cursor.execute("""
            SELECT COUNT(*) as null_count 
            FROM users 
            WHERE department_id IS NULL AND department IS NOT NULL AND department != ''
        """)
        null_count = cursor.fetchone()['null_count']
        print(f"📊 NULL department_id olan kullanıcı sayısı: {null_count}")
        
        if null_count > 0:
            print("\n🔍 NULL department_id'li kullanıcıların departmanları:")
            cursor.execute("""
                SELECT DISTINCT u.department as user_dept, 
                       CASE WHEN d.name IS NOT NULL THEN 'FOUND' ELSE 'NOT FOUND' END as status
                FROM users u
                LEFT JOIN departments d ON u.department = d.name
                WHERE u.department_id IS NULL AND u.department IS NOT NULL AND u.department != ''
            """)
            
            unmatched_depts = cursor.fetchall()
            for dept in unmatched_depts:
                status_icon = "✅" if dept['status'] == 'FOUND' else "❌"
                print(f"   {status_icon} '{dept['user_dept']}' -> {dept['status']}")
        
        # 2. Departments tablosundaki tüm departmanları listele
        print(f"\n📋 Departments tablosundaki departmanlar:")
        cursor.execute("SELECT id, name FROM departments ORDER BY name")
        departments = cursor.fetchall()
        for dept in departments:
            print(f"   {dept['id']}: '{dept['name']}'")
        
        # 3. Users tablosundaki unique departmanları listele
        print(f"\n👥 Users tablosundaki unique departmanlar:")
        cursor.execute("""
            SELECT DISTINCT department, COUNT(*) as user_count
            FROM users 
            WHERE department IS NOT NULL AND department != ''
            GROUP BY department
            ORDER BY department
        """)
        user_departments = cursor.fetchall()
        for dept in user_departments:
            print(f"   '{dept['department']}' -> {dept['user_count']} kullanıcı")
        
        # 4. Exact match kontrolü
        print(f"\n🎯 Exact Match Kontrolü:")
        cursor.execute("""
            SELECT 
                u.department as user_dept,
                d.name as dept_name,
                d.id as dept_id,
                COUNT(u.id) as user_count
            FROM users u
            LEFT JOIN departments d ON TRIM(u.department) = TRIM(d.name)
            WHERE u.department IS NOT NULL AND u.department != ''
            GROUP BY u.department, d.name, d.id
            ORDER BY u.department
        """)
        
        matches = cursor.fetchall()
        for match in matches:
            if match['dept_id']:
                print(f"   ✅ '{match['user_dept']}' -> ID: {match['dept_id']} ({match['user_count']} kullanıcı)")
            else:
                print(f"   ❌ '{match['user_dept']}' -> EŞLEŞME YOK ({match['user_count']} kullanıcı)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def fix_department_ids():
    """
    Department_id'leri düzeltir
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print("\n🔧 Department ID'leri Düzeltiliyor...")
        print("=" * 50)
        
        # TRIM kullanarak UPDATE yap
        cursor.execute("""
            UPDATE users u 
            INNER JOIN departments d ON TRIM(UPPER(u.department)) = TRIM(UPPER(d.name))
            SET u.department_id = d.id 
            WHERE u.department IS NOT NULL 
            AND u.department != ''
            AND u.department_id IS NULL
        """)
        
        updated_count = cursor.rowcount
        print(f"✅ {updated_count} kullanıcının department_id'si güncellendi (Case-insensitive)")
        
        # Sonuçları kontrol et
        cursor.execute("""
            SELECT COUNT(*) as remaining_nulls
            FROM users 
            WHERE department_id IS NULL AND department IS NOT NULL AND department != ''
        """)
        remaining = cursor.fetchone()['remaining_nulls']
        
        if remaining > 0:
            print(f"⚠️  Hala {remaining} kullanıcının department_id'si NULL")
            
            # Eşleşmeyen departmanları göster
            cursor.execute("""
                SELECT DISTINCT u.department
                FROM users u
                LEFT JOIN departments d ON TRIM(UPPER(u.department)) = TRIM(UPPER(d.name))
                WHERE u.department_id IS NULL 
                AND u.department IS NOT NULL 
                AND u.department != ''
                AND d.id IS NULL
            """)
            
            unmatched = cursor.fetchall()
            print("🔍 Eşleşmeyen departmanlar:")
            for dept in unmatched:
                print(f"   - '{dept['department']}'")
                
                # Bu departmanları departments tablosuna ekle
                cursor.execute("""
                    INSERT INTO departments (name, description, manager_id) 
                    VALUES (%s, %s, NULL)
                """, (dept['department'], f"{dept['department']} departmanı"))
                
                # Yeni eklenen department'ın ID'sini al
                new_dept_id = cursor.lastrowid
                
                # Users tablosunu güncelle
                cursor.execute("""
                    UPDATE users 
                    SET department_id = %s 
                    WHERE department = %s AND department_id IS NULL
                """, (new_dept_id, dept['department']))
                
                updated_users = cursor.rowcount
                print(f"     ✅ Departman eklendi (ID: {new_dept_id}) ve {updated_users} kullanıcı güncellendi")
        
        # Final validation
        cursor.execute("""
            SELECT COUNT(*) as total_users,
                   COUNT(department_id) as users_with_dept_id,
                   COUNT(department) as users_with_dept_name
            FROM users
        """)
        final_stats = cursor.fetchone()
        
        print(f"\n📊 Final İstatistikler:")
        print(f"   Toplam kullanıcı: {final_stats['total_users']}")
        print(f"   department_id olan: {final_stats['users_with_dept_id']}")
        print(f"   department name olan: {final_stats['users_with_dept_name']}")
        
        success_rate = (final_stats['users_with_dept_id'] / final_stats['users_with_dept_name']) * 100 if final_stats['users_with_dept_name'] > 0 else 0
        print(f"   Başarı oranı: {success_rate:.1f}%")
        
        conn.commit()
        print("\n🎉 Department ID düzeltmesi tamamlandı!")
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "fix":
        fix_department_ids()
    else:
        analyze_department_matching()
        print(f"\n💡 Eğer düzeltmek istiyorsanız: python {__file__} fix") 
