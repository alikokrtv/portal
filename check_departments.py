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
    
    print("=== DEPARTMENTS TABLE ===")
    cursor.execute("SELECT * FROM departments LIMIT 10")
    departments = cursor.fetchall()
    print(f"Found {len(departments)} departments:")
    for dept in departments:
        print(dept)
    
    print("\n=== UNIQUE DEPARTMENTS FROM USERS ===")
    cursor.execute("SELECT DISTINCT department FROM users WHERE department IS NOT NULL AND department != ''")
    user_departments = cursor.fetchall()
    print(f"Found {len(user_departments)} unique departments from users:")
    for dept in user_departments:
        print(dept['department'])
    
    print("\n=== USERS WITH DEPARTMENT INFO ===")
    cursor.execute("SELECT first_name, last_name, department FROM users WHERE department IS NOT NULL LIMIT 10")
    users = cursor.fetchall()
    for user in users:
        print(f"{user['first_name']} {user['last_name']} -> {user['department']}")
        
    conn.close()
    
except Exception as e:
    print(f"Error: {e}") 