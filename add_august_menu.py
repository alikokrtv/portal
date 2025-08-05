from app import get_db_connection
import pymysql
from datetime import datetime

conn = get_db_connection()
cursor = conn.cursor()

# Önce mevcut Ağustos menülerini sil
cursor.execute("DELETE FROM daily_menu WHERE menu_date >= '2025-08-01' AND menu_date <= '2025-08-31'")

# Ağustos 2025 menü verilerini ekle (resimden)
august_menus = [
    # 1. Hafta
    ('2025-08-01', 'Cuma', 'MERCİMEK ÇORBASI', 'KÖRİ SOSLU TAVUK', 'MEYHANE PİLAV', 'VİŞNELİ PANNA COTTA', 'YOĞURTLU MEZE', None),
    ('2025-08-02', 'Cumartesi', 'AYRAN AŞI ÇORBASI', 'SEBZELİ KÖFTE', 'ERİŞTE', 'SALATA', None, None),
    
    # 2. Hafta
    ('2025-08-05', 'Salı', 'AYRAN AŞI ÇORBASI SOĞUK', 'ŞEHRİYELİ TAVUK', 'SOGUK', 'FAVA, HUMUS ve ya MUHAMMARA', 'YOĞURTLU MEZE', 'GELENEKSEL LİMONATA'),
    ('2025-08-06', 'Çarşamba', 'ŞEHRİYELİ TAVUK ETLİ ÇORBA', 'BARBEKU SOSLU PİLİÇ', 'BULGUR PİLAV', 'SALATA', None, None),
    ('2025-08-07', 'Perşembe', 'FESLEĞENLİ DOMATES ÇORBASI', 'ETLİ KURU FASULYE', 'PİRİNÇ PİLAVI', 'TURŞU MEZE', 'GELENEKSEL AYRAN', None),
    ('2025-08-08', 'Cuma', 'EZOGELIN ÇORBASI', 'TAVUK FİNGER', 'ERİŞTE PORTAKALLI REVANİ', 'SALATA MEZE', None, None),
    ('2025-08-09', 'Cumartesi', 'AYRAN AŞI ÇORBASI', 'IZGARA KÖFTE', 'MEYHANE PİLAVI', 'GELENEKSEL LİMONATA', None, None),
    
    # 3. Hafta  
    ('2025-08-12', 'Salı', 'AYRAN AŞI ÇORBASI', 'İZMİR KÖFTE', 'SALÇALI MAKARNA', 'MEZE', 'GELENEKSEL ÇİLEKLİ LİMONATA', None),
    ('2025-08-13', 'Çarşamba', 'AYRAN AŞI ÇORBASI', 'MEYHANE PİLAVI', 'SALATA', 'FAVA, HUMUS ve ya MUHAMMARA', None, None),
    ('2025-08-14', 'Perşembe', 'AYRAN AŞI ÇORBASI', 'KREMALI MANTARLI TAVUK', 'MAKARNA', 'MEZE', 'GELENEKSEL LİMONATA', None),
    ('2025-08-15', 'Cuma', 'AYRAN AŞI ÇORBASI', 'PATATES PATLICAN MUSAKKA', 'PİRİNÇ PİLAVI', 'MAGNOLİA CUP MEZE', None, None),
    ('2025-08-16', 'Cumartesi', 'AYRAN AŞI ÇORBASI', 'TAVUK ELBASAN', 'ARPA ŞEHRİYE PİLAVI', 'SALATA', None, None),
    
    # 4. Hafta
    ('2025-08-19', 'Salı', 'YAYLA ÇORBASI', 'ETLİ NOHUT TAVA', 'ARPA ŞEHRİYELİ PİRİNÇ PİLAVI', 'SALATA MEZE', 'GELENEKSEL AYRAN', None),
    ('2025-08-20', 'Çarşamba', 'AYRAN AŞI ÇORBASI SOĞUK', 'ÇİN USULÜ PİLİÇ', 'YEŞİL MERCİMEKLİ FİRİK PİLAV', 'MEYVE', 'FAVA, HUMUS ve ya MUHAMMARA', 'GELENEKSEL LİMONATA'),
    ('2025-08-21', 'Perşembe', 'EZOGELİN ÇORBASI', 'KARIŞIK BİBER DOLMA', 'PEYNİRLİ MİLFÖY BÖREĞİ', 'YOĞURT MEZE', None, None),
    ('2025-08-22', 'Cuma', 'HAMBURGER / PATATES KIZARTMASI', None, None, 'GAZLI İÇECEK', None, None),
    ('2025-08-23', 'Cumartesi', 'AYRAN AŞI ÇORBASI', 'IZGARA TAVUK', 'KREMALI MANTARLI MAKARNA', 'SALATA', None, None),
    
    # 5. Hafta
    ('2025-08-26', 'Salı', 'KÖY ÇORBASI', 'KARNIYARIK PİRİNÇ PİLAVI', 'MEVSİM MEYVELERİ', 'MEZE', 'GELENEKSEL AYRAN', None),
    ('2025-08-27', 'Çarşamba', 'ET DÖNER / PİLAV/ LAVAS / PATATES KIZARTMASI', None, 'GAZLI İÇECEK', None, None, None),
    ('2025-08-28', 'Perşembe', 'MERCİMEK ÇORBASI', 'ETLİ KURU FASULYE', 'PİRİNÇ PİLAV', 'SALATA', 'GELENEKSEL LİMONATA', None),
    ('2025-08-29', 'Cuma', 'ERİŞTELİ YEŞİL ÇORBA', 'PİLİÇ ELBASAN TAVA', 'HAVUÇLİ PİRİNÇ PİLAV', 'ALGIDA MARAŞ CUP DONDURMA', 'MEZE', None),
    ('2025-08-30', 'Cumartesi', 'AYRAN AŞI ÇORBASI', 'DOMATES SOSLU KÖFTE', 'BULGUR PİLAVI', 'SALATA', None, None),
]

# Menüleri ekle
for menu_data in august_menus:
    cursor.execute("""
        INSERT INTO daily_menu (menu_date, day_name, soup, main_dish, side_dish, dessert, appetizer, drink, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
    """, menu_data)
    print(f"✅ {menu_data[0]} ({menu_data[1]}) menüsü eklendi")

conn.commit()
print(f"\n🎉 Ağustos 2025 menüsü tamamen eklendi! (Toplam {len(august_menus)} gün)")
conn.close()