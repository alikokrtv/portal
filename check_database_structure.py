import pymysql

# Database connection
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '255223Rtv',
    'database': 'corporate_communicator',
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("=== USERS TABLE STRUCTURE ===")
    cursor.execute("DESCRIBE users")
    users_columns = cursor.fetchall()
    for col in users_columns:
        print(f"{col['Field']}: {col['Type']} - {col['Null']} - {col['Key']} - {col['Default']}")
    
    print("\n=== DEPARTMENTS TABLE STRUCTURE ===")
    cursor.execute("DESCRIBE departments")
    dept_columns = cursor.fetchall()
    for col in dept_columns:
        print(f"{col['Field']}: {col['Type']} - {col['Null']} - {col['Key']} - {col['Default']}")
    
    print("\n=== SAMPLE DATA ANALYSIS ===")
    cursor.execute("""
        SELECT 
            u.id, u.first_name, u.last_name, u.department as user_department,
            d.id as dept_id, d.name as dept_name
        FROM users u
        LEFT JOIN departments d ON u.department = d.name
        LIMIT 10
    """)
    sample_data = cursor.fetchall()
    
    print("User -> Department Matching:")
    for row in sample_data:
        match_status = "✅ MATCHED" if row['dept_id'] else "❌ NOT MATCHED"
        print(f"{row['first_name']} {row['last_name']}: '{row['user_department']}' -> {match_status}")
    
    print("\n=== UNMATCHED DEPARTMENTS ===")
    cursor.execute("""
        SELECT DISTINCT u.department 
        FROM users u
        LEFT JOIN departments d ON u.department = d.name
        WHERE d.id IS NULL AND u.department IS NOT NULL AND u.department != ''
    """)
    unmatched = cursor.fetchall()
    print(f"Found {len(unmatched)} unmatched departments:")
    for dept in unmatched:
        print(f"- '{dept['department']}'")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}") 