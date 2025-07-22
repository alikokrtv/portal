from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'plus-kitchen-secret-key-2024'

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '255223Rtv',
    'database': 'corporate_communicator',
    'charset': 'utf8mb4'
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
        SELECT u.first_name, u.last_name, u.birth_date, u.profile_picture,
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
        SELECT u.first_name, u.last_name, u.hire_date, u.profile_picture,
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
    
    # Get pending tasks
    cursor.execute('''
        SELECT COUNT(*) as count 
        FROM tasks 
        WHERE assigned_to = %s AND status = 'pending'
    ''', (session['user_id'],))
    pending_tasks = cursor.fetchone()['count']
    
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
        JOIN users u1 ON t.created_by = u1.id 
        LEFT JOIN users u2 ON t.assigned_to = u2.id 
        WHERE t.assigned_to = %s OR t.created_by = %s
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
        SELECT u.first_name, u.last_name, u.birth_date, u.profile_picture,
               DAY(u.birth_date) as birth_day
        FROM users u 
        WHERE MONTH(u.birth_date) = MONTH(CURDATE())
        ORDER BY DAY(u.birth_date)
    ''')
    birthdays_this_month = cursor.fetchall()
    
    # All anniversaries this month
    cursor.execute('''
        SELECT u.first_name, u.last_name, u.hire_date, u.profile_picture,
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
    app.run(debug=True, host='0.0.0.0', port=6600) 