import pymysql
from datetime import datetime, date

# Database connection
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '255223Rtv',
    'database': 'corporate_communicator',
    'charset': 'utf8mb4'
}

def test_date_types():
    """
    Database'den hire_date'lerin ne tür olduğunu kontrol eder
    """
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute('''
            SELECT id, first_name, last_name, hire_date, birth_date
            FROM users 
            WHERE hire_date IS NOT NULL 
            LIMIT 5
        ''')
        
        users = cursor.fetchall()
        
        print("📅 Date Types Test")
        print("=" * 40)
        
        for user in users:
            print(f"\n👤 {user['first_name']} {user['last_name']} (ID: {user['id']})")
            
            hire_date = user['hire_date']
            birth_date = user['birth_date']
            
            print(f"   hire_date: {hire_date} (type: {type(hire_date)})")
            print(f"   birth_date: {birth_date} (type: {type(birth_date)})")
            
            # Test date conversion
            if hire_date:
                if hasattr(hire_date, 'date'):
                    hire_date_converted = hire_date.date()
                    print(f"   hire_date converted: {hire_date_converted} (type: {type(hire_date_converted)})")
                else:
                    print(f"   hire_date already date type")
                
                # Test year calculation
                today = date.today()
                if hasattr(hire_date, 'year'):
                    years_service = today.year - hire_date.year
                    print(f"   Years of service: {years_service} yıl")
        
        conn.close()
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_date_types() 