#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meeting Room Rezervasyon Sistemi Güncelleme Script'i
Bu script mevcut toplantı odası sistemini yeni modern sisteme güncelleyecek
"""

import pymysql
import os
import sys
from datetime import datetime

# Database bağlantı ayarları - Fallback password sistemi
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '255223',  # Önce 255223, sonra 255223Rtv denesin
    'database': 'corporate_communicator',
    'charset': 'utf8mb4',
    'port': 3306
}

def get_db_connection():
    """Database bağlantısı - Fallback password sistemi"""
    passwords_to_try = ['255223', '255223Rtv', '', 'root', 'admin', '123456', '2552232']
    
    for password in passwords_to_try:
        try:
            config = MYSQL_CONFIG.copy()
            config['password'] = password
            print(f"🔄 Veritabanına bağlanmaya çalışılıyor...")
            connection = pymysql.connect(**config)
            print(f"✅ Veritabanına başarıyla bağlandı!")
            return connection
        except pymysql.err.OperationalError as e:
            if "Access denied" in str(e):
                print(f"❌ Şifre reddedildi: {'[gizli]' if password else '[boş]'}")
                continue
            else:
                print(f"❌ Veritabanı bağlantı hatası: {e}")
                raise e
    
    raise Exception("❌ Hiçbir şifre ile veritabanına bağlanılamadı!")

def backup_existing_data(cursor):
    """Mevcut verileri yedekle"""
    print("💾 Mevcut veriler yedekleniyor...")
    
    try:
        # Mevcut rezervasyonları kontrol et
        cursor.execute("SELECT COUNT(*) FROM room_reservations")
        reservation_count = cursor.fetchone()[0]
        
        if reservation_count > 0:
            print(f"⚠️  {reservation_count} mevcut rezervasyon bulundu.")
            response = input("Bu verileri yedeklemek ve devam etmek istiyor musunuz? (y/n): ")
            if response.lower() != 'y':
                print("❌ İşlem iptal edildi.")
                return False
                
            # Backup timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Mevcut rezervasyonları backup et
            cursor.execute(f"""
                CREATE TABLE room_reservations_backup_{timestamp} AS 
                SELECT * FROM room_reservations
            """)
            
            cursor.execute(f"""
                CREATE TABLE meeting_rooms_backup_{timestamp} AS 
                SELECT * FROM meeting_rooms
            """)
            
            print(f"✅ Veriler room_reservations_backup_{timestamp} ve meeting_rooms_backup_{timestamp} tablolarına yedeklendi.")
        
        return True
        
    except pymysql.err.ProgrammingError:
        print("ℹ️  Henüz toplantı odası sistemi kurulmamış, doğrudan kuruluma geçiliyor.")
        return True

def update_database():
    """Database'i güncelle"""
    print("🚀 MEETING ROOM SİSTEMİ GÜNCELLENİYOR")
    print("=" * 50)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Mevcut verileri yedekle
        if not backup_existing_data(cursor):
            return False
        
        # SQL dosyasını oku ve çalıştır
        sql_file = 'create_meeting_room_system.sql'
        
        if not os.path.exists(sql_file):
            print(f"❌ {sql_file} dosyası bulunamadı!")
            return False
        
        print(f"📋 {sql_file} dosyası okunuyor...")
        
        with open(sql_file, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # SQL komutlarını ayır ve çalıştır
        sql_commands = sql_content.split(';')
        
        for i, command in enumerate(sql_commands):
            command = command.strip()
            if command:
                try:
                    print(f"⚙️  SQL komutu {i+1}/{len(sql_commands)} çalıştırılıyor...")
                    cursor.execute(command)
                    conn.commit()
                except Exception as e:
                    if "already exists" in str(e) or "Duplicate entry" in str(e):
                        print(f"ℹ️  Komut zaten uygulanmış, atlaniyor: {str(e)[:100]}...")
                    else:
                        print(f"⚠️  SQL hatası: {e}")
                        print(f"Hatalı komut: {command[:200]}...")
                        response = input("Devam etmek istiyor musunuz? (y/n): ")
                        if response.lower() != 'y':
                            raise e
        
        # Veritabanı durumunu kontrol et
        print("\n📊 DURUM KONTROLÜ")
        print("-" * 30)
        
        # Toplantı odalarını kontrol et
        cursor.execute("SELECT COUNT(*) FROM meeting_rooms")
        room_count = cursor.fetchone()[0]
        print(f"🏢 Toplantı odası sayısı: {room_count}")
        
        # Saat aralıklarını kontrol et
        cursor.execute("SELECT COUNT(*) FROM time_slots")
        slot_count = cursor.fetchone()[0]
        print(f"⏰ Saat aralığı sayısı: {slot_count}")
        
        # Rezervasyonları kontrol et
        cursor.execute("SELECT COUNT(*) FROM room_reservations")
        reservation_count = cursor.fetchone()[0]
        print(f"📅 Toplam rezervasyon sayısı: {reservation_count}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 DATABASE GÜNCELLEMESİ TAMAMLANDI!")
        print("=" * 50)
        print("✅ Yeni meeting room sistemi aktif!")
        print("🌐 Tarayıcınızdan /meeting-rooms adresine giderek test edebilirsiniz.")
        print("📧 Email bildirimleri otomatik olarak çalışacak.")
        print("🔐 Sistem herkese açık, login gerektirmez.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ GÜNCELLEME HATASI: {e}")
        print("💡 Sorun devam ederse create_meeting_room_system.sql dosyasını manuel olarak çalıştırın.")
        return False

if __name__ == "__main__":
    print("Plus Kitchen Portal - Meeting Room System Update")
    print("Bu script toplantı odası rezervasyon sistemini güncelleyecek.\n")
    
    # Güvenlik onayı
    response = input("Devam etmek istediğinizden emin misiniz? (y/n): ")
    if response.lower() != 'y':
        print("❌ İşlem iptal edildi.")
        sys.exit(0)
    
    if update_database():
        print("\n🚀 Sistem hazır! Plus Kitchen Portal toplantı rezervasyon sistemi aktif.")
    else:
        print("\n❌ Güncelleme tamamlanamadı. Lütfen hataları giderin ve tekrar deneyin.")
        sys.exit(1) 