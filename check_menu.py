from app import get_db_connection
import pymysql
from datetime import datetime

conn = get_db_connection()
cursor = conn.cursor(pymysql.cursors.DictCursor)

# Güncel menü sayısını kontrol et
cursor.execute("SELECT COUNT(*) as count FROM daily_menu WHERE menu_date >= CURDATE() AND is_active = TRUE")
result = cursor.fetchone()
print(f"Güncel menü sayısı: {result['count']}")

# Bugünün tarihini göster
print(f"Bugünün tarihi: {datetime.now().strftime('%Y-%m-%d')}")

# Mevcut menüleri listele
cursor.execute("SELECT menu_date, day_name, main_dish FROM daily_menu WHERE is_active = TRUE ORDER BY menu_date")
menus = cursor.fetchall()
print("\nMevcut menüler:")
for menu in menus:
    print(f"  {menu['menu_date']} ({menu['day_name']}) - {menu['main_dish']}")

conn.close()