import sqlite3
import time

def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

def create_file_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            expire_time INTEGER NOT NULL DEFAULT 0,
            deleted BOOLEAN NOT NULL DEFAULT 0,
            password_hash BLOB DEFAULT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_file(filename, filepath, expire_time=0, password_hash=None):
    # expiresIn is in seconds; convert to timestamp
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO files (filename, filepath, expire_time, password_hash) VALUES (?, ?, ?, ?)", (filename, filepath, expire_time, password_hash))
    conn.commit()
    conn.close()
    
def get_filepath_by_filename(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filepath FROM files WHERE filename = ? AND deleted = 0", (filename,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return None
    
    filepath = row[0]
    conn.close()
    return filepath if filepath else None

def get_password_hash(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM files WHERE filename = ? AND deleted = 0", (filename,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return row[0]



def is_file_expired(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT expire_time FROM files WHERE filename = ? AND deleted = 0", (filename,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return True
    expire_time = row[0]
    return is_expired(expire_time)

def get_all_files():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files")
    files = cursor.fetchall()
    conn.close()
    return files





def drop_files():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS files")
    conn.commit()
    conn.close()



def is_expired(expire_time):
    return time.time() > expire_time

def has_password(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM files WHERE filename = ? AND deleted = 0", (filename,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return False
    password_hash = row[0]
    return password_hash is not None