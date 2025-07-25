import pymysql

def check_promotions():
    conn = pymysql.connect(host='localhost', user='root', password='255223', database='corporate_communicator')
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute('SELECT * FROM promotions ORDER BY promotion_date DESC LIMIT 5')
    promotions = cursor.fetchall()
    
    print('Terfi verileri:')
    for p in promotions:
        print(f'- {p["employee_name"]}: {p["current_position"]} → {p["new_position"]} ({p["promotion_date"]})')
    
    conn.close()

if __name__ == "__main__":
    check_promotions() 