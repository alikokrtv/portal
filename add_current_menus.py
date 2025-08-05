from app import get_db_connection
import pymysql
from datetime import datetime, timedelta

conn = get_db_connection()
cursor = conn.cursor()

# Bugünden itibaren 7 günlük menü ekle
start_date = datetime.now().date()
menu_data = [
    {
        'date': start_date,
        'day': 'Pazartesi',
        'soup': 'DOMATES ÇORBASI',
        'main': 'IZGARA KÖFTE',
        'side': 'BULGUR PİLAVI',
        'dessert': 'MEVSİM MEYVELERİ',
        'drink': 'AYRAN',
        'appetizer': 'COBAN SALATA'
    },
    {
        'date': start_date + timedelta(days=1),
        'day': 'Salı',
        'soup': 'MERCIMEK ÇORBASI',
        'main': 'TAVUKLU PİRİNÇ',
        'side': 'TEL ŞEHRİYE',
        'dessert': 'MUHALLEBI',
        'drink': 'LİMONATA',
        'appetizer': 'MEZE TABAGI'
    },
    {
        'date': start_date + timedelta(days=2),
        'day': 'Çarşamba',
        'soup': 'YAYLA ÇORBASI',
        'main': 'TAVUK SOTE',
        'side': 'PİRİNÇ PİLAVI',
        'dessert': 'MEYVE',
        'drink': 'GAZLI İÇECEK',
        'appetizer': 'TURŞU'
    },
    {
        'date': start_date + timedelta(days=3),
        'day': 'Perşembe',
        'soup': 'TARHANA ÇORBASI',
        'main': 'ETLİ BEZELYE',
        'side': 'BULGUR PİLAVI',
        'dessert': 'TİRAMİSU',
        'drink': 'AYRAN',
        'appetizer': 'YAPRAK SARMA'
    },
    {
        'date': start_date + timedelta(days=4),
        'day': 'Cuma',
        'soup': 'SEBZE ÇORBASI',
        'main': 'BALIK FİLETO',
        'side': 'PİRİNÇ',
        'dessert': 'MEYVE SALATA',
        'drink': 'LİMONATA',
        'appetizer': 'SALATA'
    },
    {
        'date': start_date + timedelta(days=5),
        'day': 'Cumartesi',
        'soup': 'MANTAR ÇORBASI',
        'main': 'KÖFTE TAVA',
        'side': 'MAKARNA',
        'dessert': 'DÖN DONER',
        'drink': 'GAZLI İÇECEK',
        'appetizer': 'MEZE'
    },
    {
        'date': start_date + timedelta(days=6),
        'day': 'Pazar',
        'soup': 'TAVUK ÇORBASI',
        'main': 'ETLİ PATLICAN',
        'side': 'PİRİNÇ PİLAVI',
        'dessert': 'SUTLAÇ',
        'drink': 'AYRAN',
        'appetizer': 'HUMUS'
    }
]

# Önce mevcut güncel menüleri sil
cursor.execute("DELETE FROM daily_menu WHERE menu_date >= CURDATE()")

# Yeni menüleri ekle
for menu in menu_data:
    cursor.execute("""
        INSERT INTO daily_menu (menu_date, day_name, soup, main_dish, side_dish, dessert, drink, appetizer, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
    """, (
        menu['date'],
        menu['day'],
        menu['soup'],
        menu['main'],
        menu['side'],
        menu['dessert'],
        menu['drink'],
        menu['appetizer']
    ))
    print(f"✅ {menu['date']} ({menu['day']}) menüsü eklendi")

conn.commit()
print(f"\n🎉 Toplam {len(menu_data)} günlük menü eklendi!")
conn.close()