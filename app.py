from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
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
    
    # Get stats
    cursor.execute('SELECT COUNT(*) as count FROM users')
    total_users = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM announcements')
    total_announcements = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM messages WHERE receiver_id = %s AND is_read = FALSE', 
                   (session['user_id'],))
    unread_messages = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM departments')
    total_departments = cursor.fetchone()['count']
    
    # Get recent announcements
    cursor.execute('''
        SELECT a.*, u.first_name, u.last_name 
        FROM announcements a 
        JOIN users u ON a.author_id = u.id 
        ORDER BY a.created_at DESC LIMIT 5
    ''')
    announcements = cursor.fetchall()
    
    # Get upcoming birthdays (next 30 days)
    cursor.execute('''
        SELECT u.first_name, u.last_name, u.birth_date,
               DATEDIFF(
                   DATE_ADD(MAKEDATE(YEAR(CURDATE()), 1), 
                   INTERVAL (DAYOFYEAR(u.birth_date) - 1) DAY),
                   CURDATE()
               ) as days_until_birthday
        FROM users u 
        WHERE u.birth_date IS NOT NULL
        AND DATEDIFF(
            DATE_ADD(MAKEDATE(YEAR(CURDATE()), 1), 
            INTERVAL (DAYOFYEAR(u.birth_date) - 1) DAY),
            CURDATE()
        ) BETWEEN 0 AND 30
        ORDER BY days_until_birthday ASC
        LIMIT 5
    ''')
    upcoming_birthdays = cursor.fetchall()
    
    # Get upcoming work anniversaries (next 30 days)
    cursor.execute('''
        SELECT u.first_name, u.last_name, u.hire_date,
               YEAR(CURDATE()) - YEAR(u.hire_date) as years_of_service,
               DATEDIFF(
                   DATE_ADD(MAKEDATE(YEAR(CURDATE()), 1), 
                   INTERVAL (DAYOFYEAR(u.hire_date) - 1) DAY),
                   CURDATE()
               ) as days_until_anniversary
        FROM users u 
        WHERE u.hire_date IS NOT NULL
        AND DATEDIFF(
            DATE_ADD(MAKEDATE(YEAR(CURDATE()), 1), 
            INTERVAL (DAYOFYEAR(u.hire_date) - 1) DAY),
            CURDATE()
        ) BETWEEN 0 AND 30
        ORDER BY days_until_anniversary ASC
        LIMIT 5
    ''')
    upcoming_anniversaries = cursor.fetchall()
    
    # Get pending tasks - simplified
    try:
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE status = %s', ('pending',))
        pending_tasks = cursor.fetchone()['count']
    except:
        pending_tasks = 0
    
    conn.close()
    
    return render_template('dashboard.html', 
                         total_users=total_users,
                         total_announcements=total_announcements,
                         total_departments=total_departments,
                         unread_messages=unread_messages,
                         pending_tasks=pending_tasks,
                         announcements=announcements,
                         upcoming_birthdays=upcoming_birthdays,
                         upcoming_anniversaries=upcoming_anniversaries)

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
@require_login
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
    users = cursor.fetchall()
    
    cursor.execute('SELECT * FROM departments ORDER BY name')
    departments = cursor.fetchall()
    
    conn.close()
    
    return render_template('personnel.html', users=users, departments=departments)

@app.route('/departments')
@require_login
def departments():
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
    
    cursor.execute('SELECT id, first_name, last_name FROM users ORDER BY first_name, last_name')
    users = cursor.fetchall()
    
    conn.close()
    
    return render_template('departments.html', departments=departments, users=users)

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
        JOIN users u1 ON t.created_by_id = u1.id 
        LEFT JOIN users u2 ON t.assigned_to_id = u2.id 
        WHERE t.assigned_to_id = %s OR t.created_by_id = %s
        ORDER BY t.created_at DESC
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
        JOIN users u ON d.uploaded_by = u.id 
        ORDER BY d.created_at DESC
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

@app.route('/users')
@require_login
def users():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT u.*, d.name as department_name 
        FROM users u 
        LEFT JOIN departments d ON u.department_id = d.id 
        ORDER BY u.created_at DESC
    ''')
    users = cursor.fetchall()
    
    cursor.execute('SELECT * FROM departments ORDER BY name')
    departments = cursor.fetchall()
    
    conn.close()
    
    return render_template('users.html', users=users, departments=departments)

@app.route('/users/create', methods=['POST'])
@require_login
def create_user():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    department_id = request.form.get('department_id')
    position = request.form.get('position')
    
    # Hash password
    hashed_password = generate_password_hash(password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (first_name, last_name, username, email, password, department_id, position, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        ''', (first_name, last_name, username, email, hashed_password, department_id, position))
        conn.commit()
        flash('Kullanıcı başarıyla oluşturuldu!', 'success')
    except pymysql.IntegrityError:
        flash('Bu kullanıcı adı veya email zaten kullanımda!', 'error')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('users'))

@app.route('/departments/create', methods=['POST'])
@require_login
def create_department():
    name = request.form['name']
    description = request.form.get('description', '')
    manager_id = request.form.get('manager_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO departments (name, description, manager_id)
            VALUES (%s, %s, %s)
        ''', (name, description, manager_id if manager_id else None))
        conn.commit()
        flash('Departman başarıyla oluşturuldu!', 'success')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('departments'))

@app.route('/profile')
@require_login
def profile():
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

@app.route('/reports')
@require_login
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # User statistics
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)')
    new_users_month = cursor.fetchone()['count']
    
    # Department statistics
    cursor.execute('''
        SELECT d.name, COUNT(u.id) as user_count 
        FROM departments d 
        LEFT JOIN users u ON d.id = u.department_id 
        GROUP BY d.id, d.name 
        ORDER BY user_count DESC
    ''')
    dept_stats = cursor.fetchall()
    
    # Message statistics
    cursor.execute('SELECT COUNT(*) as count FROM messages WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)')
    messages_week = cursor.fetchone()['count']
    
    # Task statistics
    cursor.execute('SELECT status, COUNT(*) as count FROM tasks GROUP BY status')
    task_stats = cursor.fetchall()
    
    conn.close()
    
    return render_template('reports.html', 
                         new_users_month=new_users_month,
                         dept_stats=dept_stats,
                         messages_week=messages_week,
                         task_stats=task_stats)

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
        SELECT u.*, d.name as department_name 
        FROM users u 
        LEFT JOIN departments d ON u.department_id = d.id 
        ORDER BY u.first_name, u.last_name
    ''')
    users = cursor.fetchall()
    conn.close()
    
    return jsonify({'users': users})

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
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 6600))
    ) 