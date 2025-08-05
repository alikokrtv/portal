from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
import secrets
import uuid

# Notification service import
try:
    from notification_service import NotificationService
    notification_service = NotificationService()
except ImportError:
    print("⚠️ Notification service not available")
    notification_service = None

# Email service import
try:
    from email_service import email_service
except ImportError:
    print("⚠️ Email service not available")
    email_service = None

# Online kullanıcılar için session store
online_users = {}

def update_user_activity(user_id):
    """Kullanıcının son aktivite zamanını güncelle"""
    if user_id:
        online_users[user_id] = datetime.now()

def get_online_users():
    """Son 5 dakika içinde aktif olan kullanıcıları getir"""
    cutoff_time = datetime.now() - timedelta(minutes=5)
    active_user_ids = []
    
    # Eski kayıtları temizle
    for user_id, last_activity in list(online_users.items()):
        if last_activity < cutoff_time:
            del online_users[user_id]
        else:
            active_user_ids.append(user_id)
    
    if not active_user_ids:
        return []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Aktif kullanıcıların bilgilerini al
        placeholders = ','.join(['%s'] * len(active_user_ids))
        cursor.execute(f'''
            SELECT u.id, u.first_name, u.last_name, d.name as department_name,
                   r.name as role_name
            FROM users u
            LEFT JOIN departments d ON u.department_id = d.id
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.id
            WHERE u.id IN ({placeholders})
            ORDER BY u.first_name, u.last_name
        ''', active_user_ids)
        
        users = cursor.fetchall()
        conn.close()
        
        # Son aktivite zamanını ekle
        for user in users:
            user['last_activity'] = online_users.get(user['id'])
        
        return users
        
    except Exception as e:
        print(f"Error getting online users: {e}")
        return []

# Türkçe aylar
TURKISH_MONTHS = {
    1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran',
    7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'
}

# Load environment variables (optional)
try:
    load_dotenv()
except:
    pass  # .env file not found, using defaults

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'plus-kitchen-secret-key-2024')

# Middleware: Her istekte kullanıcı aktivitesini güncelle
@app.before_request
def before_request():
    if 'user_id' in session:
        update_user_activity(session['user_id'])

# Custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to <br> tags"""
    if text:
        return text.replace('\n', '<br>')
    return text

# MySQL Configuration - Production Ready
MYSQL_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '255223Rtv'),
    'database': os.environ.get('DB_NAME', 'corporate_communicator'),
    'charset': 'utf8mb4',
    'port': int(os.environ.get('DB_PORT', 3306))
}

# Database debugging function
def check_database_structure():
    """Veritabanı yapısını kontrol et ve hataları logla"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Tablo listesini al
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("📋 Available tables:")
        for table in tables:
            print(f"  - {list(table.values())[0]}")
        
        # Kritik tabloların yapısını kontrol et
        critical_tables = ['users', 'promotions', 'departments']
        for table_name in critical_tables:
            try:
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                print(f"\n🔍 {table_name} table structure:")
                for col in columns:
                    print(f"  - {col['Field']} ({col['Type']})")
            except Exception as e:
                print(f"❌ Error checking {table_name}: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database structure check failed: {e}")
        return False

# Database connection with fallback passwords
def get_db_connection():
    # Önce 255223Rtv (uzak sunucu), sonra 255223 (yerel) denesin
    passwords_to_try = ['255223Rtv', '255223', '', 'root', 'admin', '123456', '2552232']
    
    for password in passwords_to_try:
        try:
            config = MYSQL_CONFIG.copy()
            config['password'] = password
            print(f"🔄 Trying password: {'[empty]' if password == '' else '[hidden]'}")
            connection = pymysql.connect(**config)
            print(f"✅ Database connected successfully!")
            return connection
        except pymysql.err.OperationalError as e:
            if "Access denied" in str(e):
                print(f"❌ Access denied for password: {'[empty]' if password == '' else '[hidden]'}")
                continue
            else:
                print(f"❌ Database connection error: {e}")
                raise e
    
    # If all passwords fail, try without password
    try:
        config = MYSQL_CONFIG.copy()
        config.pop('password', None)
        print("🔄 Trying without password...")
        connection = pymysql.connect(**config)
        print("✅ Database connected without password!")
        return connection
    except Exception as e:
        print(f"❌ Final attempt failed: {e}")
        raise Exception("MySQL bağlantısı kurulamadı. MySQL sunucusunun çalışır durumda olduğundan emin olun.")

def require_login(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def require_admin(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if not session.get('is_admin', False):
            flash('Bu işlem için yönetici yetkisi gereklidir.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Kullanıcı ve rol bilgilerini al
        cursor.execute('''
            SELECT u.*, r.name as role_name, r.id as role_id
            FROM users u 
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.id
            WHERE u.username = %s
        ''', (username,))
        user = cursor.fetchone()
        conn.close()
        
        # Şifre kontrolü - hem hash hem plain text
        password_match = False
        if user:
            # Önce hash kontrolü
            if check_password_hash(user['password'], password):
                password_match = True
            # Eğer hash kontrol edilemiyorsa plain text kontrol et
            elif user['password'] == password:
                password_match = True
            # Admin için özel kontrol
            elif user['username'] == 'admin' and password == 'asd':
                password_match = True
                
        if user and password_match:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            session['email'] = user['email']
            session['department_id'] = user['department_id']  # Departman ID'sini ekle
            session['role_id'] = user.get('role_id', 18)  # Default: Standart Kullanıcı
            session['role_name'] = user.get('role_name', 'Standart Kullanıcı')
            
            # Admin veya İK yöneticisi kontrolü
            session['is_admin'] = user.get('role_name') in ['Admin', 'İK Yöneticisi', 'İçerik Yöneticisi']
            session['can_reserve_rooms'] = user.get('can_reserve_rooms', False) or session['is_admin']
            
            flash('Başarıyla giriş yaptınız!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Başarıyla çıkış yaptınız!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@require_login
def dashboard():
    # Debug: Veritabanı yapısını kontrol et
    print("🔍 Checking database structure...")
    check_database_structure()
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Recent announcements (last 5)
    cursor.execute('''
        SELECT a.*, u.first_name, u.last_name
        FROM announcements a 
        LEFT JOIN users u ON a.author_id = u.id 
        ORDER BY a.created_at DESC 
        LIMIT 5
    ''')
    announcements = cursor.fetchall()
    
    # Get upcoming birthdays (next 30 days) - Türkçe aylarla
    cursor.execute('''
        SELECT u.first_name, u.last_name, u.birth_date, d.name as department,
               CASE 
                   WHEN DATE_FORMAT(u.birth_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d') THEN 0
                   ELSE DATEDIFF(
                       DATE_ADD(MAKEDATE(YEAR(CURDATE()), 1), 
                       INTERVAL (DAYOFYEAR(u.birth_date) - 1) DAY),
                       CURDATE()
                   )
               END as days_until_birthday,
               CASE 
                   WHEN DATE_FORMAT(u.birth_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d') THEN 'Bugün'
                   ELSE CONCAT(DATEDIFF(
                       DATE_ADD(MAKEDATE(YEAR(CURDATE()), 1), 
                       INTERVAL (DAYOFYEAR(u.birth_date) - 1) DAY),
                       CURDATE()
                   ), ' gün sonra')
               END as birthday_text,
               DAY(u.birth_date) as birth_day,
               MONTH(u.birth_date) as birth_month
        FROM users u 
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE u.birth_date IS NOT NULL
        AND (
            DATE_FORMAT(u.birth_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d')
            OR DATEDIFF(
                DATE_ADD(MAKEDATE(YEAR(CURDATE()), 1), 
                INTERVAL (DAYOFYEAR(u.birth_date) - 1) DAY),
                CURDATE()
            ) BETWEEN 1 AND 30
        )
        ORDER BY days_until_birthday ASC, u.first_name
        LIMIT 5
    ''')
    upcoming_birthdays = cursor.fetchall()
    
    # Türkçe ay adlarını ekle
    for birthday in upcoming_birthdays:
        if birthday['birth_month']:
            birthday['turkish_month'] = TURKISH_MONTHS.get(birthday['birth_month'], '')
        else:
            birthday['turkish_month'] = ''
    
    # Get recent promotions (last 365 days) - carousel için daha fazla veri
    try:
        # Önce promotions tablosunun yapısını kontrol et
        cursor.execute("DESCRIBE promotions")
        promo_columns = [col['Field'] for col in cursor.fetchall()]
        print(f"📊 Promotions table columns: {promo_columns}")
        
        # Güvenli kolon seçimi
        safe_columns = []
        expected_columns = ['id', 'employee_name', 'old_position', 'new_position', 'promotion_date', 'department']
        
        for col in expected_columns:
            if col in promo_columns:
                safe_columns.append(f"p.{col}")
        
        if not safe_columns:
            safe_columns = ['p.id']  # En azından id olmalı
        
        query = f'''
            SELECT {', '.join(safe_columns)}
            FROM promotions p
            WHERE p.promotion_date >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)
            ORDER BY p.promotion_date DESC
            LIMIT 10
        '''
        
        print(f"🔍 Executing promotions query: {query}")
        cursor.execute(query)
        recent_promotions = cursor.fetchall()
        
    except Exception as e:
        print(f"❌ Promotions query error: {e}")
        recent_promotions = []

    # Get work anniversaries (next 30 days) - basitleştirilmiş hesaplama
    cursor.execute('''
        SELECT u.first_name, u.last_name, u.hire_date, d.name as department,
               TIMESTAMPDIFF(YEAR, u.hire_date, CURDATE()) as years_of_service,
               CASE 
                   WHEN DATE_FORMAT(u.hire_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d') THEN 0
                   WHEN DATE_FORMAT(u.hire_date, '%m-%d') > DATE_FORMAT(CURDATE(), '%m-%d') THEN
                       DATEDIFF(
                           DATE(CONCAT(YEAR(CURDATE()), '-', MONTH(u.hire_date), '-', DAY(u.hire_date))),
                           CURDATE()
                       )
                   ELSE
                       DATEDIFF(
                           DATE(CONCAT(YEAR(CURDATE()) + 1, '-', MONTH(u.hire_date), '-', DAY(u.hire_date))),
                           CURDATE()
                       )
               END as days_until_anniversary,
               CASE 
                   WHEN DATE_FORMAT(u.hire_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d') THEN 'Bugün'
                   WHEN DATE_FORMAT(u.hire_date, '%m-%d') > DATE_FORMAT(CURDATE(), '%m-%d') THEN
                       CONCAT(DATEDIFF(
                           DATE(CONCAT(YEAR(CURDATE()), '-', MONTH(u.hire_date), '-', DAY(u.hire_date))),
                           CURDATE()
                       ), ' gün sonra')
                   ELSE
                       CONCAT(DATEDIFF(
                           DATE(CONCAT(YEAR(CURDATE()) + 1, '-', MONTH(u.hire_date), '-', DAY(u.hire_date))),
                           CURDATE()
                       ), ' gün sonra')
               END as anniversary_text
        FROM users u 
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE u.hire_date IS NOT NULL
        AND u.hire_date < DATE_SUB(CURDATE(), INTERVAL 90 DAY)
        AND (
            (DATE_FORMAT(u.hire_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d'))
            OR 
            (DATE_FORMAT(u.hire_date, '%m-%d') > DATE_FORMAT(CURDATE(), '%m-%d') 
             AND DATEDIFF(DATE(CONCAT(YEAR(CURDATE()), '-', MONTH(u.hire_date), '-', DAY(u.hire_date))), CURDATE()) <= 30)
            OR
            (DATE_FORMAT(u.hire_date, '%m-%d') < DATE_FORMAT(CURDATE(), '%m-%d') 
             AND DATEDIFF(DATE(CONCAT(YEAR(CURDATE()) + 1, '-', MONTH(u.hire_date), '-', DAY(u.hire_date))), CURDATE()) <= 30)
        )
        ORDER BY days_until_anniversary ASC, years_of_service DESC
        LIMIT 5
    ''')
    upcoming_anniversaries = cursor.fetchall()
    
    # Basit istatistikler - intranet için gerekli olanlar
    try:
        cursor.execute('SELECT COUNT(*) as count FROM announcements')
        total_announcements = cursor.fetchone()['count']
    except:
        total_announcements = 0
        
    try:
        cursor.execute('SELECT COUNT(*) as count FROM users')
        total_personnel = cursor.fetchone()['count']
    except:
        total_personnel = 0
        
    try:
        cursor.execute('SELECT COUNT(*) as count FROM departments')
        total_departments = cursor.fetchone()['count']
    except:
        total_departments = 0
    
    # Günlük menü verilerini al (tüm personel için)
    daily_menu = []
    today_date = None
    try:
        cursor.execute('''
            SELECT menu_date, day_name, soup, main_dish, side_dish, dessert, drink, appetizer,
                   DATE(NOW()) as today
            FROM daily_menu 
            WHERE menu_date >= CURDATE() AND is_active = TRUE
            ORDER BY menu_date ASC
            LIMIT 7
        ''')
        daily_menu = cursor.fetchall()
        
        # Bugünün tarihini al
        if daily_menu:
            today_date = daily_menu[0]['today']
    except Exception as e:
        print(f"Menü verileri alınırken hata: {e}")
        daily_menu = []
    
    conn.close()
    
    return render_template('dashboard.html', 
                         announcements=announcements,
                         upcoming_birthdays=upcoming_birthdays,
                         upcoming_anniversaries=upcoming_anniversaries,
                         recent_promotions=recent_promotions,
                         total_announcements=total_announcements,
                         total_personnel=total_personnel,
                         total_departments=total_departments,
                         daily_menu=daily_menu,
                         today_date=today_date)

@app.route('/announcements')
@require_login
def announcements():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Kullanıcının departmanını al
    cursor.execute('SELECT department_id FROM users WHERE id = %s', (session['user_id'],))
    user_dept = cursor.fetchone()
    user_department_id = user_dept['department_id'] if user_dept else None
    
    # Hedeflenen duyuruları al
    cursor.execute('''
        SELECT DISTINCT a.*, u.first_name, u.last_name 
        FROM announcements a 
        JOIN users u ON a.author_id = u.id 
        WHERE a.target_type = 'all' 
           OR (a.target_type = 'department' AND FIND_IN_SET(%s, a.target_departments))
           OR (a.target_type = 'user' AND FIND_IN_SET(%s, a.target_users))
           OR (a.target_type = 'role' AND FIND_IN_SET(%s, a.target_roles))
        ORDER BY a.created_at DESC
    ''', (str(user_department_id) if user_department_id else '', str(session['user_id']), str(session.get('role_id', ''))))
    
    announcements = cursor.fetchall()
    
    # Admin için tüm duyuruları göster
    if session.get('is_admin'):
        cursor.execute('''
            SELECT a.*, u.first_name, u.last_name 
            FROM announcements a 
            JOIN users u ON a.author_id = u.id 
            ORDER BY a.created_at DESC
        ''')
        announcements = cursor.fetchall()
    
    # Hedefleme seçenekleri için veriler
    cursor.execute('SELECT id, name FROM departments ORDER BY name')
    departments = cursor.fetchall()
    
    cursor.execute('SELECT id, first_name, last_name FROM users ORDER BY first_name, last_name')
    users = cursor.fetchall()
    
    cursor.execute('SELECT id, name FROM roles ORDER BY name')
    roles = cursor.fetchall()
    
    conn.close()
    
    return render_template('announcements.html', 
                         announcements=announcements, 
                         departments=departments,
                         users=users,
                         roles=roles)

@app.route('/announcements/create', methods=['POST'])
@require_admin
def create_announcement():
    title = request.form['title']
    content = request.form['content']
    target_type = request.form.get('target_type', 'all')
    target_departments = request.form.getlist('target_departments')
    target_users = request.form.getlist('target_users')
    target_roles = request.form.getlist('target_roles')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Duyuru ekle
        cursor.execute('''
            INSERT INTO announcements (title, content, author_id, target_type, 
                                     target_departments, target_users, target_roles, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        ''', (
            title, content, session['user_id'], target_type,
            ','.join(map(str, target_departments)) if target_departments else None,
            ','.join(map(str, target_users)) if target_users else None,
            ','.join(map(str, target_roles)) if target_roles else None
        ))
        
        announcement_id = cursor.lastrowid
        
        # Hedefleme verilerini ekle
        if target_type == 'department' and target_departments:
            for dept_id in target_departments:
                cursor.execute('''
                    INSERT INTO announcement_targets (announcement_id, target_type, target_id)
                    VALUES (%s, 'department', %s)
                ''', (announcement_id, dept_id))
        elif target_type == 'user' and target_users:
            for user_id in target_users:
                cursor.execute('''
                    INSERT INTO announcement_targets (announcement_id, target_type, target_id)
                    VALUES (%s, 'user', %s)
                ''', (announcement_id, user_id))
        elif target_type == 'role' and target_roles:
            for role_id in target_roles:
                cursor.execute('''
                    INSERT INTO announcement_targets (announcement_id, target_type, target_id)
                    VALUES (%s, 'role', %s)
                ''', (announcement_id, role_id))
        
        conn.commit()
        flash('Duyuru başarıyla oluşturuldu!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Duyuru oluşturulurken hata: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('announcements'))

@app.route('/announcements/<int:id>')
@require_login
def announcement_detail(id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT a.*, u.first_name, u.last_name 
        FROM announcements a 
        JOIN users u ON a.author_id = u.id 
        WHERE a.id = %s
    ''', (id,))
    announcement = cursor.fetchone()
    conn.close()
    
    if not announcement:
        flash('Duyuru bulunamadı!', 'error')
        return redirect(url_for('announcements'))
    
    return render_template('announcement_detail.html', announcement=announcement)

@app.route('/announcements/<int:id>/edit', methods=['GET', 'POST'])
@require_admin
def edit_announcement(id):
    """Duyuru düzenle - Sadece admin"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        try:
            cursor.execute('''
                UPDATE announcements 
                SET title = %s, content = %s, updated_at = NOW()
                WHERE id = %s
            ''', (title, content, id))
            conn.commit()
            flash('Duyuru başarıyla güncellendi!', 'success')
            return redirect(url_for('announcements'))
        except Exception as e:
            conn.rollback()
            flash(f'Duyuru güncellenirken hata: {str(e)}', 'error')
    
    # GET request - form göster
    cursor.execute('''
        SELECT a.*, u.first_name, u.last_name
        FROM announcements a
        LEFT JOIN users u ON a.author_id = u.id
        WHERE a.id = %s
    ''', (id,))
    announcement = cursor.fetchone()
    
    if not announcement:
        flash('Duyuru bulunamadı!', 'error')
        return redirect(url_for('announcements'))
    
    conn.close()
    return render_template('announcement_edit.html', announcement=announcement)

@app.route('/announcements/<int:id>/delete', methods=['POST'])
@require_admin
def delete_announcement(id):
    """Duyuru sil - Sadece admin"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM announcements WHERE id = %s', (id,))
        conn.commit()
        flash('Duyuru başarıyla silindi!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Duyuru silinirken hata: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('announcements'))

# Database kolonları düzeltiliyor:
# users.department_id YOK -> users.department VAR
# users.created_at YOK -> reports için created_at kullanmıyoruz
# users.phone_number VAR -> phone yerine phone_number kullanıyoruz
# tasks.assignee_id VAR -> assigned_to_id değil
# tasks.creator_id VAR -> created_by_id değil  
# documents.uploader_id VAR -> uploaded_by değil

@app.route('/personnel')
@require_login
def personnel():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT u.*, d.name as department_name
        FROM users u 
        LEFT JOIN departments d ON u.department_id = d.id
        ORDER BY u.first_name, u.last_name
    ''')
    personnel = cursor.fetchall()
    
    cursor.execute('SELECT * FROM departments ORDER BY name')
    departments = cursor.fetchall()
    
    conn.close()
    
    return render_template('personnel.html', personnel=personnel, departments=departments, users=personnel)

@app.route('/personnel/create', methods=['POST'])
@require_admin
def create_personnel():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone_number')
        position = request.form.get('position')
        department_id = request.form.get('department_id')
        birth_date = request.form.get('birth_date')
        hire_date = request.form.get('hire_date')
        
        if not all([username, password, first_name, last_name, email]):
            flash('Zorunlu alanları doldurun!', 'error')
            return redirect(url_for('personnel'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username or email already exists
        cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
        if cursor.fetchone():
            flash('Kullanıcı adı veya email zaten kullanımda!', 'error')
            conn.close()
            return redirect(url_for('personnel'))
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO users (username, password, first_name, last_name, email, 
                             phone_number, position, department_id, birth_date, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (username, hashed_password, first_name, last_name, email, phone, 
              position, department_id if department_id else None, birth_date, hire_date))
        
        conn.commit()
        conn.close()
        
        flash('Personel başarıyla eklendi!', 'success')
        return redirect(url_for('personnel'))
        
    except Exception as e:
        flash(f'Hata: {str(e)}', 'error')
        return redirect(url_for('personnel'))

@app.route('/personnel/<int:id>')
@require_login
def personnel_detail(id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT u.*, d.name as department_name
        FROM users u 
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE u.id = %s
    ''', (id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        flash('Personel bulunamadı!', 'error')
        return redirect(url_for('personnel'))
    
    # Tarih türlerini uyumlu hale getir - mutable dict oluştur
    user = dict(user)  # Mutable dict'e çevir
    
    # hire_date'i date objesi yap
    if user.get('hire_date'):
        if hasattr(user['hire_date'], 'date'):
            # Eğer datetime ise date'e çevir
            user['hire_date'] = user['hire_date'].date()
    
    # birth_date'i de kontrol et
    if user.get('birth_date'):
        if hasattr(user['birth_date'], 'date'):
            user['birth_date'] = user['birth_date'].date()
    
    return render_template('personnel_detail.html', user=user, today=date.today())

@app.route('/personnel/<int:id>/edit', methods=['GET', 'POST'])
@require_admin
def personnel_edit(id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        position = request.form['position']
        department = request.form['department']
        phone = request.form.get('phone', '')
        role_id = request.form.get('role_id', '')
        
        # Kullanıcı bilgilerini güncelle
        cursor.execute('''
            UPDATE users 
            SET first_name = %s, last_name = %s, email = %s, 
                position = %s, department_id = %s, phone_number = %s
            WHERE id = %s
        ''', (first_name, last_name, email, position, department if department else None, phone, id))
        
        # Rol atamasını güncelle
        if role_id:
            # Mevcut rol atamasını sil
            cursor.execute('DELETE FROM user_roles WHERE user_id = %s', (id,))
            # Yeni rol atamasını ekle
            cursor.execute('INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)', (id, role_id))
        else:
            # Rol seçilmemişse mevcut rol atamasını sil
            cursor.execute('DELETE FROM user_roles WHERE user_id = %s', (id,))
        
        conn.commit()
        conn.close()
        
        flash('Personel bilgileri ve yetkileri güncellendi!', 'success')
        return redirect(url_for('personnel_detail', id=id))
    
    # GET request - form göster
    cursor.execute('''
        SELECT u.*, d.name as department_name, ur.role_id as current_role_id
        FROM users u 
        LEFT JOIN departments d ON u.department_id = d.id
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        WHERE u.id = %s
    ''', (id,))
    user = cursor.fetchone()
    
    # Departmanları getir
    cursor.execute('SELECT * FROM departments ORDER BY name')
    departments = cursor.fetchall()
    
    # Rolleri getir
    cursor.execute('SELECT * FROM roles ORDER BY name')
    roles = cursor.fetchall()
    
    conn.close()
    
    if not user:
        flash('Personel bulunamadı!', 'error')
        return redirect(url_for('personnel'))
    
    return render_template('personnel_edit.html', user=user, departments=departments, roles=roles)

@app.route('/departments')
@require_login
def departments():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT d.*, u.first_name, u.last_name,
               COUNT(emp.id) as employee_count
        FROM departments d 
        LEFT JOIN users u ON d.manager_id = u.id
        LEFT JOIN users emp ON emp.department_id = d.id
        GROUP BY d.id
        ORDER BY d.name
    ''')
    departments = cursor.fetchall()
    
    cursor.execute('SELECT id, first_name, last_name FROM users ORDER BY first_name, last_name')
    users = cursor.fetchall()
    
    conn.close()
    
    return render_template('departments.html', departments=departments, users=users)

@app.route('/departments/create', methods=['POST'])
@require_admin
def create_department():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    manager_id = request.form.get('manager_id')
    location = request.form.get('location', '').strip()
    
    if not name:
        flash('Departman adı gereklidir.', 'error')
        return redirect(url_for('departments'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO departments (name, description, manager_id, location) 
            VALUES (%s, %s, %s, %s)
        ''', (name, description if description else None, manager_id if manager_id else None, location if location else None))
        conn.commit()
        flash(f'"{name}" departmanı başarıyla eklendi!', 'success')
    except Exception as e:
        flash('Departman eklenirken bir hata oluştu. Bu isimde departman zaten var olabilir.', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('departments'))

@app.route('/departments/<int:id>/edit', methods=['GET', 'POST'])
@require_admin
def edit_department(id):
    """Departman düzenle - Sadece admin"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        manager_id = request.form.get('manager_id')
        location = request.form.get('location', '').strip()
        
        if not name:
            flash('Departman adı gereklidir.', 'error')
            return redirect(url_for('edit_department', id=id))
        
        try:
            cursor.execute('''
                UPDATE departments 
                SET name = %s, description = %s, manager_id = %s, location = %s
                WHERE id = %s
            ''', (name, description if description else None, manager_id if manager_id else None, location if location else None, id))
            conn.commit()
            flash('Departman başarıyla güncellendi!', 'success')
            return redirect(url_for('departments'))
        except Exception as e:
            conn.rollback()
            flash(f'Departman güncellenirken hata: {str(e)}', 'error')
    
    # GET request - form göster
    cursor.execute('''
        SELECT d.*, u.first_name, u.last_name
        FROM departments d
        LEFT JOIN users u ON d.manager_id = u.id
        WHERE d.id = %s
    ''', (id,))
    department = cursor.fetchone()
    
    if not department:
        flash('Departman bulunamadı!', 'error')
        return redirect(url_for('departments'))
    
    # Kullanıcıları al (manager seçimi için)
    cursor.execute('SELECT id, first_name, last_name FROM users ORDER BY first_name, last_name')
    users = cursor.fetchall()
    
    conn.close()
    return render_template('department_edit.html', department=department, users=users)

@app.route('/departments/<int:id>/delete', methods=['POST'])
@require_admin
def delete_department(id):
    """Departman sil - Sadece admin"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Önce departmanda çalışan var mı kontrol et
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE department_id = %s', (id,))
    result = cursor.fetchone()
    
    if result['count'] > 0:
        flash('Bu departmanda çalışan personel bulunduğu için silinemez!', 'error')
        conn.close()
        return redirect(url_for('departments'))
    
    try:
        cursor.execute('DELETE FROM departments WHERE id = %s', (id,))
        conn.commit()
        flash('Departman başarıyla silindi!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Departman silinirken hata: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('departments'))

@app.route('/messages')
@require_login
def messages():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT m.*, u.first_name, u.last_name 
        FROM messages m 
        JOIN users u ON m.sender_id = u.id 
        WHERE m.receiver_id = %s
        ORDER BY m.sent_at DESC
    ''', (session['user_id'],))
    messages = cursor.fetchall()
    
    cursor.execute('SELECT * FROM users WHERE id != %s ORDER BY first_name, last_name', (session['user_id'],))
    users = cursor.fetchall()
    conn.close()
    
    return render_template('messages.html', messages=messages, users=users)

@app.route('/messages/send', methods=['POST'])
@require_login
def send_message():
    receiver_id = request.form['receiver_id']
    subject = request.form['subject']
    content = request.form['content']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (sender_id, receiver_id, subject, content, is_read, created_at)
        VALUES (%s, %s, %s, %s, FALSE, NOW())
    ''', (session['user_id'], receiver_id, subject, content))
    conn.commit()
    conn.close()
    
    flash('Mesaj başarıyla gönderildi!', 'success')
    return redirect(url_for('messages'))

@app.route('/tasks')
@require_login
def tasks():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT t.*, 
               u1.first_name as creator_first_name, u1.last_name as creator_last_name,
               u2.first_name as assignee_first_name, u2.last_name as assignee_last_name
        FROM tasks t 
        JOIN users u1 ON t.creator_id = u1.id 
        LEFT JOIN users u2 ON t.assignee_id = u2.id 
        WHERE t.assignee_id = %s OR t.creator_id = %s
        ORDER BY t.due_date ASC
    ''', (session['user_id'], session['user_id']))
    tasks = cursor.fetchall()
    
    cursor.execute('SELECT id, first_name, last_name FROM users ORDER BY first_name, last_name')
    users = cursor.fetchall()
    
    conn.close()
    
    return render_template('tasks.html', tasks=tasks, users=users)

@app.route('/documents')
@require_login
def documents():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT d.*, u.first_name, u.last_name
        FROM documents d 
        LEFT JOIN users u ON d.uploader_id = u.id 
        ORDER BY d.uploaded_at DESC
    ''')
    documents = cursor.fetchall()
    
    conn.close()
    
    return render_template('documents.html', documents=documents)

@app.route('/special-days')
@require_login
def special_days():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # All birthdays this month
    cursor.execute('''
        SELECT u.first_name, u.last_name, u.birth_date,
               DAY(u.birth_date) as birth_day
        FROM users u 
        WHERE MONTH(u.birth_date) = MONTH(CURDATE())
        ORDER BY DAY(u.birth_date)
    ''')
    birthdays_this_month = cursor.fetchall()
    
    # All anniversaries this month
    cursor.execute('''
        SELECT u.first_name, u.last_name, u.hire_date,
               DAY(u.hire_date) as hire_day,
               YEAR(CURDATE()) - YEAR(u.hire_date) as years_of_service
        FROM users u 
        WHERE MONTH(u.hire_date) = MONTH(CURDATE())
        ORDER BY DAY(u.hire_date)
    ''')
    anniversaries_this_month = cursor.fetchall()
    
    conn.close()
    
    return render_template('special_days.html', 
                         birthdays=birthdays_this_month,
                         anniversaries=anniversaries_this_month)

# Users route kaldırıldı - personnel ile birleştirildi

# Duplicate create_department removed

@app.route('/profile', methods=['GET', 'POST'])
@require_login  
def profile():
    if request.method == 'POST':
        # Profil güncelleme işlemi
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Form verilerini al
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            birth_date = request.form.get('birth_date')
            hire_date = request.form.get('hire_date')
            
            # Kullanıcı bilgilerini güncelle
            cursor.execute('''
                UPDATE users 
                SET first_name = %s, last_name = %s, email = %s, phone = %s, 
                    birth_date = %s, hire_date = %s, updated_at = NOW()
                WHERE id = %s
            ''', (first_name, last_name, email, phone, birth_date, hire_date, session['user_id']))
            
            conn.commit()
            conn.close()
            
            # Session bilgilerini güncelle
            session['first_name'] = first_name
            session['last_name'] = last_name
            
            flash('Profil bilgileriniz başarıyla güncellendi!', 'success')
            return redirect(url_for('profile'))
            
        except Exception as e:
            print(f"Profil güncelleme hatası: {e}")
            flash('Profil güncellenirken bir hata oluştu!', 'error')
            return redirect(url_for('profile'))
    
    # GET isteği - profil sayfasını göster
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT u.*, d.name as department_name
        FROM users u 
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE u.id = %s
    ''', (session['user_id'],))
    user = cursor.fetchone()
    
    conn.close()
    
    return render_template('profile.html', user=user)

@app.route('/settings')
@require_login
def settings():
    return render_template('settings.html')

@app.route('/email-templates')
@require_admin
def email_templates():
    """Email template yönetimi - Sadece admin"""
    return render_template('email_templates.html')

@app.route('/api/save-email-template', methods=['POST'])
@require_admin
def save_email_template():
    """Email template kaydet - Sadece admin"""
    try:
        data = request.get_json()
        template_type = data.get('type')
        subject = data.get('subject')
        html_content = data.get('html')
        
        if not all([template_type, subject, html_content]):
            return jsonify({'success': False, 'error': 'Eksik veri'})
        
        # Template dosyasını kaydet
        template_filename = f"{template_type}_template.html"
        template_path = os.path.join('email_templates', template_filename)
        
        # Dizin yoksa oluştur
        os.makedirs('email_templates', exist_ok=True)
        
        # Template dosyasını kaydet
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return jsonify({'success': True, 'message': 'Template başarıyla kaydedildi'})
        
    except Exception as e:
        print(f"Email template kaydetme hatası: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/reports')
@require_login
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Basit istatistikler - created_at olmadığı için son 30 gün yerine toplam sayılar
    cursor.execute('SELECT COUNT(*) as count FROM users')
    total_users = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM departments')
    total_departments = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM announcements')
    total_announcements = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM messages')
    total_messages = cursor.fetchone()['count']
    
    # Departman dağılımı
    cursor.execute('''
        SELECT d.name as department, COUNT(u.id) as count 
        FROM users u 
        INNER JOIN departments d ON u.department_id = d.id
        GROUP BY d.id, d.name
        ORDER BY count DESC
    ''')
    department_distribution = cursor.fetchall()
    
    # Görev durumları
    cursor.execute('''
        SELECT status, COUNT(*) as count 
        FROM tasks 
        GROUP BY status
    ''')
    task_status = cursor.fetchall()
    
    # Terfi raporları
    cursor.execute('''
        SELECT p.*, d.name as department_name
        FROM promotions p
        LEFT JOIN departments d ON p.department = d.name
        ORDER BY p.promotion_date DESC
    ''')
    promotions = cursor.fetchall()
    
    # Terfi istatistikleri
    cursor.execute('''
        SELECT 
            COUNT(*) as total_promotions,
            COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_promotions,
            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_promotions
        FROM promotions
    ''')
    promotion_stats = cursor.fetchone()
    
    conn.close()
    
    # Varsayılan değerler (created_at kolonu olmadığı için)
    new_users_month = 0  # Bu ay yeni kullanıcı yok
    
    return render_template('reports.html', 
                         total_users=total_users,
                         total_departments=total_departments, 
                         total_announcements=total_announcements,
                         total_messages=total_messages,
                         department_distribution=department_distribution,
                         task_status=task_status,
                         new_users_month=new_users_month,
                         promotions=promotions,
                         promotion_stats=promotion_stats)

# API Endpoints

# --------------------
# ✅ NEW: User profile endpoint
@app.route('/api/user/profile')
@require_login
def api_user_profile():
    """Return basic profile info for the logged-in user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT id, first_name, last_name, email
            FROM users
            WHERE id = %s
        """, (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        if not user:
            return jsonify({}), 404
        return jsonify(user), 200
    except Exception as e:
        print(f"api_user_profile error: {e}")
        return jsonify({'error': 'Server error'}), 500

# --------------------
# ✅ NEW: All users endpoint (for participant list)
@app.route('/api/users/all')
@require_login
def api_users_all():
    """Return list of all users (id, first_name, last_name)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT id, first_name, last_name
            FROM users
            ORDER BY first_name, last_name
        """)
        users = cursor.fetchall()
        conn.close()
        return jsonify(users), 200
    except Exception as e:
        print(f"api_users_all error: {e}")
        return jsonify({'error': 'Server error'}), 500

# --------------------
# ✅ NEW: All future reservations for a room (list below calendar)
@app.route('/api/room-reservations/all/<int:room_id>')
@require_login
def api_room_reservations_all(room_id):
    """Return all future reservations for the given room."""
    try:
        today_str = date.today().isoformat()
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT rr.id, rr.date, rr.start_time, rr.end_time,
                   CONCAT(u.first_name, ' ', u.last_name) AS requester_name,
                   rr.purpose
            FROM room_reservations rr
            LEFT JOIN users u ON rr.requester_id = u.id
            WHERE rr.room_id = %s AND rr.date >= %s
            ORDER BY rr.date, rr.start_time
        """, (room_id, today_str))
        reservations = cursor.fetchall()
        conn.close()
        return jsonify(reservations), 200
    except Exception as e:
        print(f"api_room_reservations_all error: {e}")
        return jsonify({'error': 'Server error'}), 500

# --------------------
# ✅ NEW: Notification unread count placeholder
@app.route('/api/notifications/unread-count')
@require_login
def api_notifications_unread_count():
    """Return unread notification count (placeholder)."""
    # TODO: replace with real notification table logic
    return jsonify({'unread': 0}), 200
@app.route('/api/messages/unread/count')
@require_login
def api_unread_messages():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT COUNT(*) as count FROM messages WHERE receiver_id = %s AND is_read = FALSE', 
                   (session['user_id'],))
    count = cursor.fetchone()['count']
    conn.close()
    
    return jsonify({'count': count})

@app.route('/api/messages/<int:message_id>/read', methods=['POST'])
@require_login
def api_mark_message_read(message_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE messages SET is_read = TRUE WHERE id = %s AND receiver_id = %s', 
                   (message_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})



@app.route('/api/departments')
@require_login
def api_departments():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT d.*, 
               COUNT(u.id) as employee_count,
               m.first_name as manager_first_name,
               m.last_name as manager_last_name
        FROM departments d 
        LEFT JOIN users u ON d.id = u.department_id 
        LEFT JOIN users m ON d.manager_id = m.id
        GROUP BY d.id
        ORDER BY d.name
    ''')
    departments = cursor.fetchall()
    conn.close()
    
    return jsonify({'departments': departments})

@app.route('/jobs')
@require_login  
def jobs():
    """Açık pozisyonlar listesi - Admin için yönetim, diğerleri için görüntüleme"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Açık pozisyonları al
    cursor.execute('''
        SELECT j.*, d.name as department_name, u.first_name, u.last_name
        FROM jobs j
        LEFT JOIN departments d ON j.department_id = d.id
        LEFT JOIN users u ON j.posted_by = u.id
        WHERE j.status = 'active'
        ORDER BY j.posted_date DESC
    ''')
    jobs_list = cursor.fetchall()
    
    # Departmanları al (admin için)
    cursor.execute('SELECT id, name FROM departments ORDER BY name')
    departments = cursor.fetchall()
    
    conn.close()
    
    return render_template('jobs.html', jobs=jobs_list, departments=departments)

@app.route('/jobs/create', methods=['POST'])
@require_admin
def create_job():
    """Yeni iş ilanı oluştur - Sadece admin"""
    title = request.form['title']
    department_id = request.form['department_id']
    location = request.form['location']
    job_type = request.form['job_type']
    description = request.form['description']
    requirements = request.form.get('requirements', '')
    external_link = request.form.get('external_link', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO jobs (title, department_id, location, job_type, description, requirements, posted_by, posted_date, status, external_link)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), 'active', %s)
        ''', (title, department_id, location, job_type, description, requirements, session['user_id'], external_link))
        conn.commit()
        flash('İş ilanı başarıyla oluşturuldu!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'İş ilanı oluşturulurken hata: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('jobs'))

@app.route('/jobs/<int:id>/edit', methods=['GET', 'POST'])
@require_admin
def edit_job(id):
    """İş ilanı düzenle - Sadece admin"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    if request.method == 'POST':
        title = request.form['title']
        department_id = request.form['department_id']
        location = request.form['location']
        job_type = request.form['job_type']
        description = request.form['description']
        requirements = request.form.get('requirements', '')
        status = request.form.get('status', 'active')
        
        try:
            cursor.execute('''
                UPDATE jobs 
                SET title = %s, department_id = %s, location = %s, job_type = %s, 
                    description = %s, requirements = %s, status = %s, updated_date = NOW()
                WHERE id = %s
            ''', (title, department_id, location, job_type, description, requirements, status, id))
            conn.commit()
            flash('İş ilanı başarıyla güncellendi!', 'success')
            return redirect(url_for('jobs'))
        except Exception as e:
            conn.rollback()
            flash(f'İş ilanı güncellenirken hata: {str(e)}', 'error')
    
    # GET request - form göster
    cursor.execute('''
        SELECT j.*, d.name as department_name
        FROM jobs j
        LEFT JOIN departments d ON j.department_id = d.id
        WHERE j.id = %s
    ''', (id,))
    job = cursor.fetchone()
    
    if not job:
        flash('İş ilanı bulunamadı!', 'error')
        return redirect(url_for('jobs'))
    
    # Departmanları al
    cursor.execute('SELECT id, name FROM departments ORDER BY name')
    departments = cursor.fetchall()
    
    conn.close()
    return render_template('job_edit.html', job=job, departments=departments)

@app.route('/jobs/<int:id>/delete', methods=['POST'])
@require_admin
def delete_job(id):
    """İş ilanı sil - Sadece admin"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM jobs WHERE id = %s', (id,))
        conn.commit()
        flash('İş ilanı başarıyla silindi!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'İş ilanı silinirken hata: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('jobs'))

# Meeting Room Routes
@app.route('/meeting-rooms')
def meeting_rooms():
    """Modern toplantı odası rezervasyon sayfası - Herkese açık"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Toplantı odalarını al
    cursor.execute('SELECT * FROM meeting_rooms WHERE is_active = TRUE ORDER BY name')
    rooms = cursor.fetchall()
    
    # Saat aralıklarını al
    cursor.execute('SELECT * FROM time_slots WHERE is_active = TRUE ORDER BY sort_order')
    time_slots = cursor.fetchall()
    
    # Bugünden itibaren 30 günlük rezervasyonları al
    cursor.execute('''
        SELECT r.*, mr.name as room_name,
               COALESCE(CONCAT(u.first_name, " ", u.last_name), r.requester_name) as user_name
        FROM room_reservations r
        JOIN meeting_rooms mr ON r.room_id = mr.id
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.reservation_date >= CURDATE()
        AND r.reservation_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        AND r.status != 'cancelled'
        ORDER BY r.reservation_date, r.start_time
    ''')
    reservations = cursor.fetchall()
    
    conn.close()
    return render_template('meeting_rooms.html', rooms=rooms, reservations=reservations, time_slots=time_slots)

@app.route('/meeting-rooms/reserve', methods=['POST'])
def reserve_room():
    """Modern toplantı odası rezervasyonu yap - Login gerektirmez"""
    room_id = request.form['room_id']
    reservation_date = request.form['reservation_date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    requester_name = request.form['requester_name']
    requester_surname = request.form.get('requester_surname', '')
    requester_email = request.form['requester_email']
    requester_phone = request.form.get('requester_phone', '')
    attendees_count = request.form.get('attendees_count', 1)
    purpose = request.form.get('purpose', '')
    notes = request.form.get('notes', '')
    
    # Full name oluştur
    full_name = f"{requester_name} {requester_surname}".strip()
    
    # Confirmation code oluştur
    confirmation_code = str(uuid.uuid4())[:8].upper()
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Çakışma kontrolü
        cursor.execute('''
            SELECT COUNT(*) as conflict_count
            FROM room_reservations 
            WHERE room_id = %s 
            AND reservation_date = %s
            AND status != 'cancelled'
            AND (
                (start_time <= %s AND end_time > %s) OR
                (start_time < %s AND end_time >= %s) OR
                (start_time >= %s AND end_time <= %s)
            )
        ''', (room_id, reservation_date, start_time, start_time, end_time, end_time, start_time, end_time))
        
        conflict = cursor.fetchone()['conflict_count']
        
        if conflict > 0:
            return jsonify({'success': False, 'message': 'Seçtiğiniz saatte oda zaten rezerve edilmiş!'})
        
        # Oda bilgilerini al
        cursor.execute('SELECT name FROM meeting_rooms WHERE id = %s', (room_id,))
        room = cursor.fetchone()
        room_name = room['name'] if room else 'Bilinmeyen Oda'
        
        # Rezervasyonu kaydet
        cursor.execute('''
            INSERT INTO room_reservations 
            (room_id, user_id, reservation_date, start_time, end_time, purpose, 
             attendees_count, requester_name, requester_email, requester_phone, 
             notes, confirmation_code, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'approved')
        ''', (room_id, session.get('user_id') or None, reservation_date, start_time, end_time, 
              purpose, attendees_count, full_name, requester_email, requester_phone, 
              notes, confirmation_code))
        
        reservation_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Rezervasyon başarıyla oluşturuldu - ID: {reservation_id}, Kod: {confirmation_code}")
        print(f"📊 Detaylar: {full_name} - {room_name} - {reservation_date} {start_time}-{end_time}")
        
        # Email gönder
        try:
            if email_service:
                date_formatted = datetime.strptime(reservation_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                    <div style="background: linear-gradient(135deg, #00b4a6, #007991); color: white; padding: 30px; text-align: center;">
                        <h1 style="margin: 0; font-size: 24px;">✅ Rezervasyonunuz Onaylandı!</h1>
                    </div>
                    
                    <div style="padding: 30px;">
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">Sevgili <strong>{full_name}</strong>,</p>
                        
                        <p style="font-size: 16px; color: #333; line-height: 1.6;">
                            Toplantı odası rezervasyonunuz başarıyla oluşturuldu. Rezervasyon detaylarınız aşağıdadır:
                        </p>
                        
                        <div style="background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 20px 0; border-left: 4px solid #00b4a6;">
                            <h3 style="color: #00b4a6; margin-top: 0;">📋 Rezervasyon Detayları</h3>
                            <p style="margin: 5px 0;"><strong>📍 Oda:</strong> {room_name}</p>
                            <p style="margin: 5px 0;"><strong>📅 Tarih:</strong> {date_formatted}</p>
                            <p style="margin: 5px 0;"><strong>⏰ Saat:</strong> {start_time} - {end_time}</p>
                            <p style="margin: 5px 0;"><strong>👥 Katılımcı Sayısı:</strong> {attendees_count}</p>
                            <p style="margin: 5px 0;"><strong>🔢 Rezervasyon Kodu:</strong> <span style="background: #e3f2fd; padding: 4px 8px; border-radius: 4px; font-family: monospace;">{confirmation_code}</span></p>
                            {f'<p style="margin: 5px 0;"><strong>📝 Amaç:</strong> {purpose}</p>' if purpose else ''}
                        </div>
                        
                        <div style="background: #fff3e0; border-radius: 10px; padding: 15px; margin: 20px 0; border-left: 4px solid #ff9800;">
                            <h4 style="color: #f57c00; margin-top: 0;">📞 İletişim</h4>
                            <p style="margin: 5px 0; color: #666;">Herhangi bir sorunuz olursa bizimle iletişime geçebilirsiniz:</p>
                            <p style="margin: 5px 0; color: #666;"><strong>📧 Email:</strong> portal@pluskitchen.com.tr</p>
                            <p style="margin: 5px 0; color: #666;"><strong>📱 Telefon:</strong> 0212 XXX XX XX</p>
                        </div>
                        
                        <p style="color: #666; font-size: 14px; text-align: center; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                            Teşekkür ederiz,<br>
                            <strong>Plus Kitchen Portal</strong><br>
                            <a href="https://portal.pluskitchen.com.tr" style="color: #00b4a6; text-decoration: none;">https://portal.pluskitchen.com.tr</a>
                        </p>
                    </div>
                </div>
                """
                
                email_service.send_email(
                    to_email=requester_email,
                    subject="✅ Toplantı Odası Rezervasyon Onayı",
                    html_content=html_content
                )
        except Exception as e:
            print(f"Email gönderme hatası: {e}")
        
        return jsonify({
            'success': True, 
            'message': 'Rezervasyonunuz başarıyla oluşturuldu! Onay bilgileri e-mail adresinize gönderildi.',
            'confirmation_code': confirmation_code,
            'booking_id': reservation_id
        })
        
    except Exception as e:
        conn.rollback()
        print(f"Rezervasyon hatası: {e}")
        return jsonify({'success': False, 'message': f'Rezervasyon oluşturulurken hata oluştu: {str(e)}'})
    finally:
        conn.close()

@app.route('/meeting-rooms/cancel/<int:id>')
@require_login  
def cancel_reservation(id):
    """Rezervasyonu iptal et"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Rezervasyonu kontrol et - sadece kendi rezervasyonunu veya admin iptal edebilir
    cursor.execute('''
        SELECT user_id FROM room_reservations WHERE id = %s
    ''', (id,))
    reservation = cursor.fetchone()
    
    if not reservation:
        flash('Rezervasyon bulunamadı!', 'error')
    elif reservation['user_id'] != session['user_id'] and not session.get('is_admin'):
        flash('Bu rezervasyonu iptal etme yetkiniz yok!', 'error')
    else:
        cursor.execute('''
            UPDATE room_reservations SET status = 'cancelled' WHERE id = %s
        ''', (id,))
        conn.commit()
        flash('Rezervasyon başarıyla iptal edildi!', 'success')
    
    conn.close()
    return redirect(url_for('meeting_rooms'))

@app.route('/api/room-reservations/<int:room_id>/<date>')
def get_room_reservations(room_id, date):
    """Belirli bir oda ve tarih için rezervasyonları JSON olarak döndür"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print(f"🔍 API Call: Room {room_id}, Date {date}")
        
        cursor.execute('''
            SELECT r.start_time, r.end_time, r.purpose, r.reservation_date,
                   COALESCE(CONCAT(u.first_name, " ", u.last_name), r.requester_name) as user_name,
                   r.requester_name, u.first_name, u.last_name
            FROM room_reservations r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.room_id = %s 
            AND r.reservation_date = %s
            AND r.status != 'cancelled'
            ORDER BY r.start_time
        ''', (room_id, date))
        
        reservations = cursor.fetchall()
        conn.close()
        
        print(f"📊 Found {len(reservations)} reservations")
        
        # Time objelerini string'e çevir
        for res in reservations:
            if res['start_time']:
                # Farklı time formatlarını handle et
                if hasattr(res['start_time'], 'strftime'):
                    res['start_time'] = res['start_time'].strftime('%H:%M')
                else:
                    # String ise :00 kısmını kaldır
                    time_str = str(res['start_time'])
                    if time_str.endswith(':00'):
                        res['start_time'] = time_str[:-3]
                    else:
                        res['start_time'] = time_str
                    
            if res['end_time']:
                if hasattr(res['end_time'], 'strftime'):
                    res['end_time'] = res['end_time'].strftime('%H:%M')
                else:
                    # String ise :00 kısmını kaldır
                    time_str = str(res['end_time'])
                    if time_str.endswith(':00'):
                        res['end_time'] = time_str[:-3]
                    else:
                        res['end_time'] = time_str
        
        print(f"📋 Returning: {reservations}")
        return jsonify(reservations)
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify([]), 500

@app.route('/api/room-reservations/month/<int:room_id>/<int:year>/<int:month>')
def get_monthly_room_reservations(room_id, year, month):
    """Belirli bir oda ve ay için tüm rezervasyonları JSON olarak döndür"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print(f"🗓️ Monthly API Call: Room {room_id}, Year {year}, Month {month}")
        
        # Ayın ilk ve son günü
        first_day = f"{year}-{month:02d}-01"
        if month == 12:
            last_day = f"{year + 1}-01-01"
        else:
            last_day = f"{year}-{month + 1:02d}-01"
        
        cursor.execute('''
            SELECT r.start_time, r.end_time, r.purpose, r.reservation_date,
                   COALESCE(CONCAT(u.first_name, " ", u.last_name), r.requester_name) as user_name,
                   r.requester_name, u.first_name, u.last_name
            FROM room_reservations r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.room_id = %s 
            AND r.reservation_date >= %s
            AND r.reservation_date < %s
            AND r.status != 'cancelled'
            ORDER BY r.reservation_date, r.start_time
        ''', (room_id, first_day, last_day))
        
        reservations = cursor.fetchall()
        conn.close()
        
        print(f"📊 Found {len(reservations)} monthly reservations")
        
        # Time objelerini string'e çevir ve date formatını düzelt
        for res in reservations:
            if res['start_time']:
                if hasattr(res['start_time'], 'strftime'):
                    res['start_time'] = res['start_time'].strftime('%H:%M')
                else:
                    time_str = str(res['start_time'])
                    if time_str.endswith(':00'):
                        res['start_time'] = time_str[:-3]
                    else:
                        res['start_time'] = time_str
                    
            if res['end_time']:
                if hasattr(res['end_time'], 'strftime'):
                    res['end_time'] = res['end_time'].strftime('%H:%M')
                else:
                    time_str = str(res['end_time'])
                    if time_str.endswith(':00'):
                        res['end_time'] = time_str[:-3]
                    else:
                        res['end_time'] = time_str
            
            # Reservation date'i string format'a çevir
            if res['reservation_date']:
                if hasattr(res['reservation_date'], 'strftime'):
                    res['reservation_date'] = res['reservation_date'].strftime('%Y-%m-%d')
                else:
                    # Eğer datetime string ise sadece date kısmını al
                    date_str = str(res['reservation_date'])
                    res['reservation_date'] = date_str.split(' ')[0]
        
        print(f"📋 Returning monthly: {reservations}")
        return jsonify(reservations)
        
    except Exception as e:
        print(f"❌ Monthly API Error: {e}")
        return jsonify([]), 500

@app.route('/meeting-rooms/confirmation/<confirmation_code>')
def reservation_confirmation(confirmation_code):
    """Rezervasyon onay sayfası"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute('''
        SELECT r.*, mr.name as room_name
        FROM room_reservations r
        JOIN meeting_rooms mr ON r.room_id = mr.id
        WHERE r.confirmation_code = %s
    ''', (confirmation_code,))
    
    reservation = cursor.fetchone()
    conn.close()
    
    if not reservation:
        return render_template('reservation_not_found.html'), 404
    
    return render_template('reservation_confirmation.html', reservation=reservation)

# Notification API Endpoints
@app.route('/api/notifications')
@require_login
def get_notifications():
    """Kullanıcının bildirimlerini getir"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Kullanıcının bildirimlerini al (son 50 adet)
        cursor.execute('''
            SELECT n.*, COALESCE(nt.name, 'general') as type_name
            FROM notifications n
            LEFT JOIN notification_types nt ON n.type_id = nt.id
            WHERE n.user_id = %s
            ORDER BY n.created_at DESC
            LIMIT 50
        ''', (session['user_id'],))
        
        notifications = cursor.fetchall()
        
        # Okunmamış bildirimleri say
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM notifications
            WHERE user_id = %s AND status IN ('pending', 'sent')
        ''', (session['user_id'],))
        
        unread_count = cursor.fetchone()['count']
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/notifications/unread-count')
@require_login
def get_unread_count():
    """Okunmamış bildirim sayısını getir"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM notifications
            WHERE user_id = %s AND status IN ('pending', 'sent')
        ''', (session['user_id'],))
        
        result = cursor.fetchone()
        count = result['count'] if result else 0
        
        return jsonify({'success': True, 'count': count})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/notifications/mark-read/<int:notification_id>', methods=['POST'])
@require_login
def mark_notification_read(notification_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET status = 'read', read_at = NOW()
            WHERE id = %s AND user_id = %s
        ''', (notification_id, session['user_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/online-users')
@require_login
def api_online_users():
    """Online kullanıcıları döndür (sadece admin ve İK yöneticileri)"""
    # Yetki kontrolü
    if not session.get('is_admin') and session.get('role_name') != 'İK Yöneticisi':
        return jsonify({'success': False, 'error': 'Yetkiniz yok'}), 403
    
    try:
        online_users_list = get_online_users()
        
        return jsonify({
            'success': True,
            'online_users': online_users_list,
            'count': len(online_users_list),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notifications/mark-all-read', methods=['POST'])
@require_login
def mark_all_notifications_read():
    """Tüm bildirimleri okundu olarak işaretle"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE notifications 
            SET status = 'read', read_at = NOW()
            WHERE user_id = %s AND status IN ('pending', 'sent')
        ''', (session['user_id'],))
        
        conn.commit()
        updated_count = cursor.rowcount
        
        return jsonify({
            'success': True, 
            'message': f'{updated_count} bildirim okundu işaretlendi'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/admin/notifications')
@require_admin
def admin_notifications():
    """Admin bildirim gönderme sayfası"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Departmanları al
        cursor.execute('SELECT id, name FROM departments ORDER BY name')
        departments = cursor.fetchall()
        
        return render_template('admin_notifications.html', departments=departments)
        
    except Exception as e:
        flash(f'Sayfa yüklenirken hata: {str(e)}', 'error')
        return redirect(url_for('dashboard'))
    finally:
        conn.close()

@app.route('/api/users')
@require_login
def api_users():
    """Kullanıcı listesi API"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Sadece admin veya İK departmanı kullanıcıları bu API'yi kullanabilir
        if not session.get('is_admin'):
            cursor.execute('SELECT department_id FROM users WHERE id = %s', (session['user_id'],))
            user_dept = cursor.fetchone()
            if not user_dept or user_dept['department_id'] != 1:  # 1 = İK departmanı
                return jsonify({'error': 'Yetkisiz erişim'}), 403
        
        cursor.execute('''
            SELECT u.id, u.first_name, u.last_name, u.position, u.email, u.phone_number,
                   d.name as department_name
            FROM users u
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE u.is_active = TRUE
            ORDER BY u.first_name, u.last_name
        ''')
        
        users = cursor.fetchall()
        return jsonify({'success': True, 'users': users})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/admin/send-notification', methods=['POST'])
@require_admin
def api_send_admin_notification():
    """Admin bildirim gönderme API"""
    if not notification_service:
        return jsonify({'success': False, 'error': 'Notification service not available'}), 500
    
    try:
        data = request.get_json()
        
        recipient_type = data.get('recipient_type')
        recipients = data.get('recipients', [])
        title = data.get('title')
        message = data.get('message')
        priority = data.get('priority', 'normal')
        channels = data.get('channels', {})
        send_timing = data.get('send_timing', 'now')
        scheduled_time = data.get('scheduled_time')
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Alıcı listesini belirle
        target_users = []
        
        if recipient_type == 'all':
            # Herkese gönder
            cursor.execute('SELECT id FROM users WHERE is_active = TRUE')
            target_users = [row['id'] for row in cursor.fetchall()]
            
        elif recipient_type == 'departments':
            # Belirli departmanlara gönder
            dept_ids = [r.replace('dept_', '') for r in recipients if r.startswith('dept_')]
            if dept_ids:
                placeholders = ','.join(['%s'] * len(dept_ids))
                cursor.execute(f'''
                    SELECT id FROM users 
                    WHERE department_id IN ({placeholders}) AND is_active = TRUE
                ''', dept_ids)
                target_users = [row['id'] for row in cursor.fetchall()]
                
        elif recipient_type == 'users':
            # Belirli kullanıcılara gönder
            user_ids = [r.replace('user_', '') for r in recipients if r.startswith('user_')]
            target_users = [int(uid) for uid in user_ids]
        
        conn.close()
        
        if not target_users:
            return jsonify({'success': False, 'error': 'Hedef kullanıcı bulunamadı'})
        
        # Bildirimleri gönder
        sent_count = 0
        from datetime import datetime
        scheduled_at = None
        
        if send_timing == 'scheduled' and scheduled_time:
            scheduled_at = datetime.fromisoformat(scheduled_time.replace('T', ' '))
        
        # Her kanal için gönder
        for user_id in target_users:
            variables = notification_service.get_user_variables(user_id)
            
            if channels.get('in_app'):
                success = notification_service.create_notification(
                    user_id=user_id,
                    notification_type='general_announcement',
                    channel='in_app',
                    variables={**variables, 'title': title, 'message': message},
                    scheduled_at=scheduled_at
                )
                if success:
                    sent_count += 1
            
            if channels.get('email'):
                success = notification_service.create_notification(
                    user_id=user_id,
                    notification_type='general_announcement',
                    channel='email',
                    variables={**variables, 'title': title, 'message': message},
                    scheduled_at=scheduled_at
                )
                if success:
                    sent_count += 1
            
            if channels.get('whatsapp'):
                success = notification_service.create_notification(
                    user_id=user_id,
                    notification_type='general_announcement',
                    channel='whatsapp',
                    variables={**variables, 'title': title, 'message': message},
                    scheduled_at=scheduled_at
                )
                if success:
                    sent_count += 1
        
        return jsonify({
            'success': True,
            'sent_count': sent_count,
            'target_users': len(target_users)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/test-notifications')
@require_admin
def test_notifications():
    """Test bildirimleri oluştur (sadece admin)"""
    if not notification_service:
        return "Notification service not available", 500
    
    try:
        # Test doğum günü bildirimi
        success = notification_service.create_notification(
            user_id=session['user_id'],
            notification_type='birthday',
            channel='in_app',
            variables={'first_name': session['first_name'], 'last_name': session['last_name']}
        )
        
        if success:
            flash('Test bildirimi oluşturuldu!', 'success')
        else:
            flash('Test bildirimi oluşturulamadı!', 'error')
            
    except Exception as e:
        flash(f'Test bildirimi hatası: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

# ======================================
# PASSWORD RESET ROUTES
# ======================================

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Şifremi unuttum sayfası"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('E-posta adresi gerekli', 'error')
            return render_template('forgot_password.html')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # Kullanıcıyı e-posta ile bul
            cursor.execute("SELECT id, first_name, last_name, email FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                # Token oluştur
                token = str(uuid.uuid4())
                expires_at = datetime.now() + timedelta(hours=1)  # 1 saat geçerli
                
                # Eski tokenları temizle
                cursor.execute("DELETE FROM password_reset_tokens WHERE user_id = %s", (user['id'],))
                
                # Yeni token kaydet
                cursor.execute("""
                    INSERT INTO password_reset_tokens (user_id, token, expires_at) 
                    VALUES (%s, %s, %s)
                """, (user['id'], token, expires_at))
                
                conn.commit()
                
                # E-posta gönder
                if email_service:
                    reset_link = f"http://portal.pluskitchen.com.tr/reset-password/{token}"
                    user_name = f"{user['first_name']} {user['last_name']}"
                    
                    success = email_service.send_password_reset_email(
                        user['email'],
                        reset_link,
                        user_name
                    )
                    
                    if success:
                        flash('Şifre sıfırlama bağlantısı e-posta adresinize gönderildi', 'success')
                    else:
                        flash('E-posta gönderilirken hata oluştu, lütfen daha sonra tekrar deneyin', 'error')
                else:
                    flash('E-posta servisi mevcut değil', 'error')
            else:
                # Güvenlik için her zaman başarı mesajı göster
                flash('Eğer bu e-posta sistemde kayıtlı ise, şifre sıfırlama bağlantısı gönderildi', 'success')
            
            conn.close()
            
        except Exception as e:
            print(f"Password reset error: {e}")
            flash('Bir hata oluştu, lütfen daha sonra tekrar deneyin', 'error')
            
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Yeni şifre belirleme sayfası"""
    token_valid = False
    user = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Token kontrolü
        cursor.execute("""
            SELECT prt.*, u.id as user_id, u.first_name, u.last_name, u.email 
            FROM password_reset_tokens prt
            JOIN users u ON prt.user_id = u.id
            WHERE prt.token = %s AND prt.expires_at > NOW() AND prt.used_at IS NULL
        """, (token,))
        
        token_data = cursor.fetchone()
        
        if token_data:
            token_valid = True
            user = token_data
            
            if request.method == 'POST':
                password = request.form.get('password', '')
                confirm_password = request.form.get('confirm_password', '')
                
                if not password or not confirm_password:
                    flash('Tüm alanları doldurun', 'error')
                elif password != confirm_password:
                    flash('Şifreler eşleşmiyor', 'error')
                elif len(password) < 8:
                    flash('Şifre en az 8 karakter olmalı', 'error')
                else:
                    # Şifreyi güncelle
                    hashed_password = generate_password_hash(password)
                    
                    cursor.execute("UPDATE users SET password = %s WHERE id = %s", 
                                 (hashed_password, user['user_id']))
                    
                    # Token'ı kullanıldı olarak işaretle
                    cursor.execute("UPDATE password_reset_tokens SET used_at = NOW() WHERE token = %s", (token,))
                    
                    conn.commit()
                    
                    flash('Şifreniz başarıyla güncellendi. Giriş yapabilirsiniz.', 'success')
                    return redirect(url_for('login'))
        
        conn.close()
        
    except Exception as e:
        print(f"Reset password error: {e}")
        flash('Bir hata oluştu', 'error')
    
    return render_template('reset_password.html', token_valid=token_valid)

@app.route('/find-account', methods=['GET', 'POST'])
def find_account():
    """Hesap bulma sayfası - Kişisel bilgilerle hesap bulma"""
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        birth_date = request.form.get('birth_date', '').strip()
        
        if not all([first_name, last_name, birth_date]):
            flash('Tüm alanları doldurun', 'error')
            return render_template('find_account.html')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # Kullanıcıyı bul
            cursor.execute("""
                SELECT id, username, first_name, last_name, email, birth_date
                FROM users 
                WHERE LOWER(first_name) = LOWER(%s) 
                AND LOWER(last_name) = LOWER(%s) 
                AND birth_date = %s
            """, (first_name, last_name, birth_date))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                # Güvenlik için doğrudan şifre göstermek yerine şifre sıfırlama token'ı oluştur
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Token oluştur
                token = str(uuid.uuid4())
                expires_at = datetime.now() + timedelta(hours=1)
                
                # Eski tokenları temizle
                cursor.execute("DELETE FROM password_reset_tokens WHERE user_id = %s", (user['id'],))
                
                # Yeni token kaydet
                cursor.execute("""
                    INSERT INTO password_reset_tokens (user_id, token, expires_at) 
                    VALUES (%s, %s, %s)
                """, (user['id'], token, expires_at))
                
                conn.commit()
                conn.close()
                
                # Reset linki oluştur
                reset_link = f"http://portal.pluskitchen.com.tr/reset-password/{token}"
                
                return render_template('find_account.html', 
                                     user_found=True, 
                                     user=user, 
                                     reset_link=reset_link)
            else:
                flash('Girdiğiniz bilgilerle eşleşen bir hesap bulunamadı', 'error')
                
        except Exception as e:
            print(f"Find account error: {e}")
            flash('Bir hata oluştu, lütfen daha sonra tekrar deneyin', 'error')
    
    return render_template('find_account.html', user_found=False)

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=80,
        load_dotenv=False  # .env problemi için devre dışı
    ) 