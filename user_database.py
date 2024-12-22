import sqlite3

def setup_database():
    conn = sqlite3.connect('soundcloud_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checked_users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            permalink_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def is_user_checked(user_id):
    conn = sqlite3.connect('soundcloud_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM checked_users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def update_database(user_id, username, permalink_url):
    conn = sqlite3.connect('soundcloud_users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO checked_users (user_id, username, permalink_url)
        VALUES (?, ?, ?)
    ''', (user_id, username, permalink_url))
    conn.commit()
    conn.close()

def get_all_entries():
    conn = sqlite3.connect('soundcloud_users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM checked_users')
    entries = cursor.fetchall()
    conn.close()
    return entries