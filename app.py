from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'plus-kitchen-secret-key-2024'

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            department TEXT,
            position TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Announcements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            subject TEXT,
            content TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    ''')
    
    # Create default admin user
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, department, position)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@pluskitchen.com', admin_password, 'Admin', 'User', 'Yönetim', 'Sistem Yöneticisi'))
    
    conn.commit()
    conn.close()

# Helper functions
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

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
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
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
    
    # Get stats
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_announcements = conn.execute('SELECT COUNT(*) as count FROM announcements').fetchone()['count']
    unread_messages = conn.execute('SELECT COUNT(*) as count FROM messages WHERE receiver_id = ? AND is_read = FALSE', 
                                 (session['user_id'],)).fetchone()['count']
    
    # Get recent announcements
    announcements = conn.execute('''
        SELECT a.*, u.first_name, u.last_name 
        FROM announcements a 
        JOIN users u ON a.author_id = u.id 
        ORDER BY a.created_at DESC LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         total_users=total_users,
                         total_announcements=total_announcements,
                         unread_messages=unread_messages,
                         announcements=announcements)

@app.route('/announcements')
@require_login
def announcements():
    conn = get_db_connection()
    announcements = conn.execute('''
        SELECT a.*, u.first_name, u.last_name 
        FROM announcements a 
        JOIN users u ON a.author_id = u.id 
        ORDER BY a.created_at DESC
    ''').fetchall()
    conn.close()
    
    return render_template('announcements.html', announcements=announcements)

@app.route('/announcements/create', methods=['POST'])
@require_login
def create_announcement():
    title = request.form['title']
    content = request.form['content']
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO announcements (title, content, author_id)
        VALUES (?, ?, ?)
    ''', (title, content, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Duyuru başarıyla oluşturuldu!', 'success')
    return redirect(url_for('announcements'))

@app.route('/messages')
@require_login
def messages():
    conn = get_db_connection()
    messages = conn.execute('''
        SELECT m.*, u.first_name, u.last_name 
        FROM messages m 
        JOIN users u ON m.sender_id = u.id 
        WHERE m.receiver_id = ?
        ORDER BY m.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    users = conn.execute('SELECT * FROM users WHERE id != ?', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('messages.html', messages=messages, users=users)

@app.route('/messages/send', methods=['POST'])
@require_login
def send_message():
    receiver_id = request.form['receiver_id']
    subject = request.form['subject']
    content = request.form['content']
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO messages (sender_id, receiver_id, subject, content)
        VALUES (?, ?, ?, ?)
    ''', (session['user_id'], receiver_id, subject, content))
    conn.commit()
    conn.close()
    
    flash('Mesaj başarıyla gönderildi!', 'success')
    return redirect(url_for('messages'))

@app.route('/users')
@require_login
def users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY first_name, last_name').fetchall()
    conn.close()
    
    return render_template('users.html', users=users)

# API Endpoints
@app.route('/api/messages/unread/count')
@require_login
def api_unread_messages():
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) as count FROM messages WHERE receiver_id = ? AND is_read = FALSE', 
                        (session['user_id'],)).fetchone()['count']
    conn.close()
    
    return jsonify({'count': count})

@app.route('/api/messages/<int:message_id>/read', methods=['POST'])
@require_login
def api_mark_message_read(message_id):
    conn = get_db_connection()
    conn.execute('UPDATE messages SET is_read = TRUE WHERE id = ? AND receiver_id = ?', 
                (message_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=6600) 