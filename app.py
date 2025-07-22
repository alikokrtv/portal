from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables (optional)
try:
    load_dotenv()
except:
    pass  # .env file not found, using defaults

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'plus-kitchen-secret-key-2024')

# MySQL Configuration - Production Ready
MYSQL_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '255223Rtv'),
    'database': os.environ.get('DB_NAME', 'corporate_communicator'),
    'charset': 'utf8mb4',
    'port': int(os.environ.get('DB_PORT', 3306))
}

# Database connection
def get_db_connection():
    return pymysql.connect(**MYSQL_CONFIG)

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
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            session['email'] = user['email']
            session['role_id'] = user.get('role_id', 18)  # Default: Standart Kullanıcı
            session['role_name'] = user.get('role_name', 'Standart Kullanıcı')
            
            # Admin veya İK yöneticisi kontrolü
            session['is_admin'] = user.get('role_name') in ['Admin', 'İK Yöneticisi', 'İçerik Yöneticisi']
            
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
    
    # Get upcoming birthdays (next 30 days) - bugün olanları farklı göster
    cursor.execute('''
        SELECT u.first_name, u.last_name, u.birth_date,
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
               END as birthday_text
        FROM users u 
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
    
    # Get work anniversaries (next 30 days) - bugün olanları farklı göster
    cursor.execute('''
        SELECT u.first_name, u.last_name, u.hire_date, u.department,
               YEAR(CURDATE()) - YEAR(u.hire_date) as years_of_service,
               CASE 
                   WHEN DATE_FORMAT(u.hire_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d') THEN 0
                   ELSE DATEDIFF(
                       DATE_ADD(MAKEDATE(YEAR(CURDATE()), 1), 
                       INTERVAL (DAYOFYEAR(u.hire_date) - 1) DAY),
                       CURDATE()
                   )
               END as days_until_anniversary,
               CASE 
                   WHEN DATE_FORMAT(u.hire_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d') THEN 'Bugün'
                   ELSE CONCAT(DATEDIFF(
                       DATE_ADD(MAKEDATE(YEAR(CURDATE()), 1), 
                       INTERVAL (DAYOFYEAR(u.hire_date) - 1) DAY),
                       CURDATE()
                   ), ' gün sonra')
               END as anniversary_text
        FROM users u 
        WHERE u.hire_date IS NOT NULL
        AND u.hire_date <= CURDATE()
        AND (
            DATE_FORMAT(u.hire_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d')
            OR DATEDIFF(
                DATE_ADD(MAKEDATE(YEAR(CURDATE()), 1), 
                INTERVAL (DAYOFYEAR(u.hire_date) - 1) DAY),
                CURDATE()
            ) BETWEEN 1 AND 30
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
    
    conn.close()
    
    return render_template('dashboard.html', 
                         announcements=announcements,
                         upcoming_birthdays=upcoming_birthdays,
                         upcoming_anniversaries=upcoming_anniversaries,
                         total_announcements=total_announcements,
                         total_personnel=total_personnel,
                         total_departments=total_departments)

@app.route('/announcements')
@require_login
def announcements():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT a.*, u.first_name, u.last_name 
        FROM announcements a 
        JOIN users u ON a.author_id = u.id 
        ORDER BY a.created_at DESC
    ''')
    announcements = cursor.fetchall()
    conn.close()
    
    return render_template('announcements.html', announcements=announcements)

@app.route('/announcements/create', methods=['POST'])
@require_admin
def create_announcement():
    title = request.form['title']
    content = request.form['content']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO announcements (title, content, author_id, created_at)
        VALUES (%s, %s, %s, NOW())
    ''', (title, content, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Duyuru başarıyla oluşturuldu!', 'success')
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
        LEFT JOIN departments d ON u.department = d.name
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
        department_name = request.form.get('department_name')
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
                             phone_number, position, department, birth_date, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (username, hashed_password, first_name, last_name, email, phone, 
              position, department_name, birth_date, hire_date))
        
        conn.commit()
        conn.close()
        
        flash('Personel başarıyla eklendi!', 'success')
        return redirect(url_for('personnel'))
        
    except Exception as e:
        flash(f'Hata: {str(e)}', 'error')
        return redirect(url_for('personnel'))

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
        LEFT JOIN users emp ON emp.department = d.name
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
        ORDER BY m.created_at DESC
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

@app.route('/profile')
@require_login  
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT u.*, d.name as department_name
        FROM users u 
        LEFT JOIN departments d ON u.department = d.name
        WHERE u.id = %s
    ''', (session['user_id'],))
    user = cursor.fetchone()
    
    conn.close()
    
    return render_template('profile.html', user=user)

@app.route('/settings')
@require_login
def settings():
    return render_template('settings.html')

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
        SELECT u.department, COUNT(*) as count 
        FROM users u 
        WHERE u.department IS NOT NULL 
        GROUP BY u.department 
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
    
    conn.close()
    
    return render_template('reports.html', 
                         total_users=total_users,
                         total_departments=total_departments, 
                         total_announcements=total_announcements,
                         total_messages=total_messages,
                         department_distribution=department_distribution,
                         task_status=task_status)

# API Endpoints
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

@app.route('/api/users')
@require_login
def api_users():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT u.id, u.first_name, u.last_name, u.department
        FROM users u 
        ORDER BY u.first_name, u.last_name
    ''')
    users = cursor.fetchall()
    
    conn.close()
    
    return jsonify(users)

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

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=6600,
        load_dotenv=False  # .env problemi için devre dışı
    ) 