#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import schedule
import time
import sys
import os
from datetime import datetime

# Project path'ini ekle
sys.path.append('.')

try:
    from notification_service import run_daily_notifications
    print("✅ Notification service imported successfully")
except ImportError as e:
    print(f"❌ Failed to import notification service: {e}")
    sys.exit(1)

def job():
    """Günlük bildirim işini çalıştır"""
    print(f"\n🚀 Starting daily notification job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        total_sent = run_daily_notifications()
        print(f"✅ Daily notification job completed. Total notifications sent: {total_sent}")
    except Exception as e:
        print(f"❌ Daily notification job failed: {e}")

def main():
    """Ana scheduler loop'u"""
    print("🎯 Plus Kitchen Notification Scheduler Started")
    print("=" * 50)
    
    # Her gün saat 09:00'da çalıştır
    schedule.every().day.at("09:00").do(job)
    
    # Hatırlatmaları her gün saat 17:00'de gönder (bir gün öncesinden)
    schedule.every().day.at("17:00").do(job)
    
    # Test için her saat başı da çalıştırabilirsiniz (geliştirme için)
    # schedule.every().hour.do(job)
    
    print("📅 Scheduled tasks:")
    print("   • Daily notifications: 09:00")
    print("   • Department reminders: 17:00")
    print("\n⏰ Scheduler is running... Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user")
    except Exception as e:
        print(f"\n❌ Scheduler error: {e}")

if __name__ == '__main__':
    main() 