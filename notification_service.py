#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional
import os
import sys

sys.path.append('.')
from app import get_db_connection

class NotificationService:
    def __init__(self):
        # Email ayarları
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.email_user = os.environ.get('EMAIL_USER', 'pluskitchen@gmail.com')
        self.email_password = os.environ.get('EMAIL_PASSWORD', 'app_password_here')
        
        # WhatsApp API ayarları (örnek: WhatsApp Business API)
        self.whatsapp_api_url = os.environ.get('WHATSAPP_API_URL', 'https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages')
        self.whatsapp_token = os.environ.get('WHATSAPP_TOKEN', 'your_whatsapp_token_here')
        
    def render_template(self, template: str, variables: Dict) -> str:
        """Template'i değişkenlerle render et"""
        rendered = template
        for key, value in variables.items():
            placeholder = f'{{{{{key}}}}}'
            rendered = rendered.replace(placeholder, str(value))
        return rendered
    
    def get_template(self, notification_type: str, channel: str) -> Optional[Dict]:
        """Bildirim template'ini getir"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT nt.subject, nt.body_template
                FROM notification_templates nt
                JOIN notification_types typ ON nt.type_id = typ.id
                WHERE typ.name = %s AND nt.channel = %s AND nt.is_active = TRUE
                LIMIT 1
            ''', (notification_type, channel))
            
            result = cursor.fetchone()
            if result:
                return {
                    'subject': result[0],
                    'body': result[1]
                }
            return None
        finally:
            conn.close()
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Email gönder"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            print(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Email send failed to {to_email}: {e}")
            return False
    
    def send_whatsapp(self, phone_number: str, message: str) -> bool:
        """WhatsApp mesajı gönder"""
        try:
            # Telefon numarasını temizle (sadece rakamlar)
            clean_phone = re.sub(r'[^\d]', '', phone_number)
            if not clean_phone.startswith('90'):
                clean_phone = '90' + clean_phone
            
            headers = {
                'Authorization': f'Bearer {self.whatsapp_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messaging_product': 'whatsapp',
                'to': clean_phone,
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            response = requests.post(
                self.whatsapp_api_url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ WhatsApp sent to {phone_number}")
                return True
            else:
                print(f"❌ WhatsApp send failed to {phone_number}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ WhatsApp send failed to {phone_number}: {e}")
            return False
    
    def create_notification(self, user_id: int, notification_type: str, 
                          channel: str, variables: Dict = None, 
                          scheduled_at: datetime = None) -> bool:
        """Bildirim oluştur"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Notification type ID'sini al
            cursor.execute('SELECT id FROM notification_types WHERE name = %s', (notification_type,))
            type_result = cursor.fetchone()
            if not type_result:
                print(f"❌ Notification type not found: {notification_type}")
                return False
            
            type_id = type_result[0]
            
            # Template'i al
            template = self.get_template(notification_type, channel)
            if not template:
                print(f"❌ Template not found for {notification_type} - {channel}")
                return False
            
            # Variables'ı render et
            if variables is None:
                variables = {}
                
            title = self.render_template(template['subject'] or '', variables)
            message = self.render_template(template['body'], variables)
            
            # Bildirim kaydet
            cursor.execute('''
                INSERT INTO notifications 
                (user_id, type_id, title, message, channel, scheduled_at, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, type_id, title, message, channel, 
                  scheduled_at, json.dumps(variables)))
            
            notification_id = cursor.lastrowid
            conn.commit()
            
            # Eğer hemen gönderilecekse gönder
            if scheduled_at is None or scheduled_at <= datetime.now():
                return self.send_notification(notification_id)
            
            print(f"✅ Notification scheduled: {notification_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create notification: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def send_notification(self, notification_id: int) -> bool:
        """Bildirimi gönder"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Bildirim ve kullanıcı bilgilerini al
            cursor.execute('''
                SELECT n.*, u.email, u.phone_number, u.first_name, u.last_name
                FROM notifications n
                JOIN users u ON n.user_id = u.id
                WHERE n.id = %s AND n.status = 'pending'
            ''', (notification_id,))
            
            notification = cursor.fetchone()
            if not notification:
                print(f"❌ Notification not found or already sent: {notification_id}")
                return False
            
            # Unpack notification data
            (n_id, user_id, type_id, title, message, channel, status, 
             scheduled_at, sent_at, read_at, metadata, created_at, updated_at,
             email, phone_number, first_name, last_name) = notification
            
            success = False
            
            # Kanal tipine göre gönder
            if channel == 'email' and email:
                success = self.send_email(email, title, message)
            elif channel == 'whatsapp' and phone_number:
                success = self.send_whatsapp(phone_number, message)
            elif channel == 'in_app':
                # Site içi bildirim için status'u 'sent' yap
                success = True
            
            # Status'u güncelle
            new_status = 'sent' if success else 'failed'
            sent_time = datetime.now() if success else None
            
            cursor.execute('''
                UPDATE notifications 
                SET status = %s, sent_at = %s
                WHERE id = %s
            ''', (new_status, sent_time, notification_id))
            
            conn.commit()
            
            if success:
                print(f"✅ Notification sent successfully: {notification_id}")
            else:
                print(f"❌ Notification send failed: {notification_id}")
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to send notification {notification_id}: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_variables(self, user_id: int) -> Dict:
        """Kullanıcı değişkenlerini al"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT u.*, d.name as department_name
                FROM users u
                LEFT JOIN departments d ON u.department_id = d.id
                WHERE u.id = %s
            ''', (user_id,))
            
            user = cursor.fetchone()
            if not user:
                return {}
            
            # Unpack user data
            (user_id, username, email, password_hash, first_name, last_name, 
             phone_number, department_id, position, birth_date, hire_date, 
             profile_picture, is_admin, is_active, created_at, updated_at, department_name) = user
            
            variables = {
                'first_name': first_name or '',
                'last_name': last_name or '',
                'email': email or '',
                'phone_number': phone_number or '',
                'position': position or '',
                'department_name': department_name or '',
                'birth_date': birth_date.strftime('%d/%m/%Y') if birth_date else '',
                'hire_date': hire_date.strftime('%d/%m/%Y') if hire_date else ''
            }
            
            # İş yılı hesapla
            if hire_date:
                years = (datetime.now().date() - hire_date).days // 365
                variables['years'] = str(years)
            
            return variables
            
        except Exception as e:
            print(f"❌ Failed to get user variables: {e}")
            return {}
        finally:
            conn.close()
    
    def send_birthday_notifications(self) -> int:
        """Bugün doğum günü olan kişilere bildirim gönder"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Bugün doğum günü olanları bul
            cursor.execute('''
                SELECT id, first_name, last_name
                FROM users 
                WHERE DATE_FORMAT(birth_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d')
                AND is_active = TRUE
            ''')
            
            birthday_users = cursor.fetchall()
            sent_count = 0
            
            for user_id, first_name, last_name in birthday_users:
                print(f"🎂 Sending birthday notifications for {first_name} {last_name}")
                
                variables = self.get_user_variables(user_id)
                
                # Email, WhatsApp ve site içi bildirim gönder
                channels = ['email', 'whatsapp', 'in_app']
                
                for channel in channels:
                    success = self.create_notification(
                        user_id=user_id,
                        notification_type='birthday',
                        channel=channel,
                        variables=variables
                    )
                    if success:
                        sent_count += 1
            
            return sent_count
            
        except Exception as e:
            print(f"❌ Failed to send birthday notifications: {e}")
            return 0
        finally:
            conn.close()
    
    def send_anniversary_notifications(self) -> int:
        """Bugün iş yıl dönümü olan kişilere bildirim gönder"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Bugün iş yıl dönümü olanları bul (en az 1 yıl geçmiş olmalı)
            cursor.execute('''
                SELECT id, first_name, last_name, hire_date
                FROM users 
                WHERE DATE_FORMAT(hire_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d')
                AND hire_date < DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                AND is_active = TRUE
            ''')
            
            anniversary_users = cursor.fetchall()
            sent_count = 0
            
            for user_id, first_name, last_name, hire_date in anniversary_users:
                years = (datetime.now().date() - hire_date).days // 365
                print(f"🏆 Sending anniversary notifications for {first_name} {last_name} ({years} years)")
                
                variables = self.get_user_variables(user_id)
                
                # Email, WhatsApp ve site içi bildirim gönder
                channels = ['email', 'whatsapp', 'in_app']
                
                for channel in channels:
                    success = self.create_notification(
                        user_id=user_id,
                        notification_type='work_anniversary',
                        channel=channel,
                        variables=variables
                    )
                    if success:
                        sent_count += 1
            
            return sent_count
            
        except Exception as e:
            print(f"❌ Failed to send anniversary notifications: {e}")
            return 0
        finally:
            conn.close()
    
    def send_promotion_notification(self, user_id: int, new_position: str, 
                                  promotion_date: str) -> bool:
        """Terfi bildirimi gönder"""
        try:
            variables = self.get_user_variables(user_id)
            variables.update({
                'new_position': new_position,
                'promotion_date': promotion_date
            })
            
            # Email, WhatsApp ve site içi bildirim gönder
            channels = ['email', 'whatsapp', 'in_app']
            success_count = 0
            
            for channel in channels:
                success = self.create_notification(
                    user_id=user_id,
                    notification_type='promotion',
                    channel=channel,
                    variables=variables
                )
                if success:
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Failed to send promotion notification: {e}")
            return False
    
    def send_department_reminders(self) -> int:
        """Departman yöneticilerine yarın doğum günü/yıl dönümü hatırlatması gönder"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            sent_count = 0
            
            # Yarın doğum günü olanları bul
            cursor.execute('''
                SELECT u.id, u.first_name, u.last_name, u.birth_date, u.department_id, d.name as department_name
                FROM users u
                LEFT JOIN departments d ON u.department_id = d.id
                WHERE DATE_FORMAT(u.birth_date, '%m-%d') = DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL 1 DAY), '%m-%d')
                AND u.is_active = TRUE
            ''')
            
            tomorrow_birthdays = cursor.fetchall()
            
            for user_id, first_name, last_name, birth_date, dept_id, dept_name in tomorrow_birthdays:
                # Departman yöneticilerini bul (örnek: İK departmanı)
                cursor.execute('''
                    SELECT id, first_name, last_name, email
                    FROM users 
                    WHERE (department_id = 1 OR is_admin = TRUE) 
                    AND is_active = TRUE
                    AND email IS NOT NULL
                ''')
                
                managers = cursor.fetchall()
                
                for manager_id, manager_first_name, manager_last_name, manager_email in managers:
                    variables = {
                        'manager_name': f"{manager_first_name} {manager_last_name}",
                        'first_name': first_name,
                        'last_name': last_name,
                        'birth_date': birth_date.strftime('%d/%m/%Y') if birth_date else '',
                        'department_name': dept_name or 'Bilinmeyen Departman'
                    }
                    
                    success = self.create_notification(
                        user_id=manager_id,
                        notification_type='birthday_reminder',
                        channel='email',
                        variables=variables
                    )
                    if success:
                        sent_count += 1
            
            # Yarın iş yıl dönümü olanları bul
            cursor.execute('''
                SELECT u.id, u.first_name, u.last_name, u.hire_date, u.department_id, d.name as department_name
                FROM users u
                LEFT JOIN departments d ON u.department_id = d.id
                WHERE DATE_FORMAT(u.hire_date, '%m-%d') = DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL 1 DAY), '%m-%d')
                AND u.hire_date < DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                AND u.is_active = TRUE
            ''')
            
            tomorrow_anniversaries = cursor.fetchall()
            
            for user_id, first_name, last_name, hire_date, dept_id, dept_name in tomorrow_anniversaries:
                years = (datetime.now().date() - hire_date).days // 365
                
                # Departman yöneticilerini bul
                cursor.execute('''
                    SELECT id, first_name, last_name, email
                    FROM users 
                    WHERE (department_id = 1 OR is_admin = TRUE) 
                    AND is_active = TRUE
                    AND email IS NOT NULL
                ''')
                
                managers = cursor.fetchall()
                
                for manager_id, manager_first_name, manager_last_name, manager_email in managers:
                    variables = {
                        'manager_name': f"{manager_first_name} {manager_last_name}",
                        'first_name': first_name,
                        'last_name': last_name,
                        'hire_date': hire_date.strftime('%d/%m/%Y') if hire_date else '',
                        'years': str(years),
                        'department_name': dept_name or 'Bilinmeyen Departman'
                    }
                    
                    success = self.create_notification(
                        user_id=manager_id,
                        notification_type='anniversary_reminder',
                        channel='email',
                        variables=variables
                    )
                    if success:
                        sent_count += 1
            
            return sent_count
            
        except Exception as e:
            print(f"❌ Failed to send department reminders: {e}")
            return 0
        finally:
            conn.close()
    
    def process_pending_notifications(self) -> int:
        """Bekleyen bildirimleri işle"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Gönderilmesi gereken bildirimleri al
            cursor.execute('''
                SELECT id FROM notifications 
                WHERE status = 'pending' 
                AND (scheduled_at IS NULL OR scheduled_at <= NOW())
                ORDER BY created_at ASC
                LIMIT 50
            ''')
            
            pending_notifications = cursor.fetchall()
            processed_count = 0
            
            for (notification_id,) in pending_notifications:
                success = self.send_notification(notification_id)
                if success:
                    processed_count += 1
            
            return processed_count
            
        except Exception as e:
            print(f"❌ Failed to process pending notifications: {e}")
            return 0
        finally:
            conn.close()

# Ana fonksiyonlar
def run_daily_notifications():
    """Günlük bildirim işlemlerini çalıştır"""
    print("🚀 Starting daily notification process...")
    
    service = NotificationService()
    
    # Doğum günü bildirimleri
    birthday_count = service.send_birthday_notifications()
    print(f"🎂 Birthday notifications sent: {birthday_count}")
    
    # İş yıl dönümü bildirimleri  
    anniversary_count = service.send_anniversary_notifications()
    print(f"🏆 Anniversary notifications sent: {anniversary_count}")
    
    # Departman hatırlatmaları
    reminder_count = service.send_department_reminders()
    print(f"📋 Department reminders sent: {reminder_count}")
    
    # Bekleyen bildirimleri işle
    pending_count = service.process_pending_notifications()
    print(f"📤 Pending notifications processed: {pending_count}")
    
    total = birthday_count + anniversary_count + reminder_count + pending_count
    print(f"✅ Total notifications processed: {total}")
    
    return total

if __name__ == '__main__':
    run_daily_notifications() 