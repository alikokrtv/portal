import pymysql

# Database connection
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '255223Rtv',
    'database': 'corporate_communicator',
    'charset': 'utf8mb4'
}

# Unique departmanları users tablosundan al ve departments tablosuna ekle
try:
    conn = pymysql.connect(**config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Önce mevcut departmanları kontrol et
    cursor.execute("SELECT name FROM departments")
    existing_departments = [row['name'] for row in cursor.fetchall()]
    print(f"Mevcut departmanlar: {existing_departments}")
    
    # Users tablosundan unique departmanları al
    cursor.execute("""
        SELECT DISTINCT department 
        FROM users 
        WHERE department IS NOT NULL 
        AND department != '' 
        AND department NOT IN (SELECT name FROM departments)
        ORDER BY department
    """)
    
    new_departments = cursor.fetchall()
    print(f"\nEklenecek {len(new_departments)} yeni departman:")
    
    # Her departmanı ekle
    for dept in new_departments:
        dept_name = dept['department']
        print(f"Ekleniyor: {dept_name}")
        
        cursor.execute("""
            INSERT INTO departments (name, description, manager_id) 
            VALUES (%s, %s, %s)
        """, (dept_name, f"{dept_name} departmanı", None))
    
    # Değişiklikleri kaydet
    conn.commit()
    print(f"\n✅ {len(new_departments)} departman başarıyla eklendi!")
    
    # Sonucu kontrol et
    cursor.execute("SELECT COUNT(*) as total FROM departments")
    total = cursor.fetchone()['total']
    print(f"Toplam departman sayısı: {total}")
    
    cursor.execute("SELECT * FROM departments ORDER BY name")
    all_departments = cursor.fetchall()
    print("\n=== TÜM DEPARTMANLAR ===")
    for dept in all_departments:
        print(f"ID: {dept['id']}, Ad: {dept['name']}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    if 'conn' in locals():
        conn.rollback()
        conn.close() 