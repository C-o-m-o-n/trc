import sqlite3
import os
from datetime import datetime

DB_NAME = "trc_history.db"

def init_db():
    """Initialize the SQLite database and create tables if they don't exist"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create messages table
    # timetoken is UNIQUE to prevent duplicate storage during reconnections
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT NOT NULL,
            user TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            timetoken TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Create channels metadata table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            name TEXT PRIMARY KEY,
            topic TEXT,
            updated_at TEXT
        )
    ''')
    
    # Create local settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_message(channel, user, message, timestamp, timetoken):
    """Save a single message to the database. Returns True if saved, False if duplicate."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (channel, user, message, timestamp, timetoken)
            VALUES (?, ?, ?, ?, ?)
        ''', (channel, user, message, timestamp, timetoken))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # This happens if timetoken already exists (duplicate prevention)
        return False
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

def get_local_history(channel, limit=50):
    """Retrieve the latest messages for a channel from the local database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user, message, timestamp, timetoken 
            FROM messages 
            WHERE channel = ? 
            ORDER BY id DESC 
            LIMIT ?
        ''', (channel, limit))
        rows = cursor.fetchall()
        
        # Convert to list of dicts and reverse so they are in chronological order
        messages = []
        for row in rows:
            messages.append({
                "user": row[0],
                "message": row[1],
                "timestamp": row[2],
                "timetoken": row[3]
            })
        messages.reverse()
        return messages
    except Exception as e:
        print(f"Database fetch error: {e}")
        return []
    finally:
        conn.close()

def clear_channel_history(channel):
    """Delete all local history for a specific channel"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM messages WHERE channel = ?', (channel,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Database clear error: {e}")
        return False
    finally:
        conn.close()

def set_channel_topic(channel, topic):
    """Set the topic for a channel"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO channels (name, topic, updated_at) 
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET topic=excluded.topic, updated_at=excluded.updated_at
        ''', (channel, topic, now))
        conn.commit()
        return True
    except Exception as e:
        print(f"Database topic error: {e}")
        return False
    finally:
        conn.close()

def get_channel_topic(channel):
    """Get the current topic for a channel"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT topic FROM channels WHERE name = ?', (channel,))
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Database fetch topic error: {e}")
        return None
    finally:
        conn.close()

def update_setting(key, value):
    """Update a local setting (e.g., 'nick')"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO settings (key, value) 
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        ''', (key, str(value)))
        conn.commit()
        return True
    except Exception as e:
        print(f"Database setting error: {e}")
        return False
    finally:
        conn.close()

def get_setting(key, default=None):
    """Get a local setting"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row[0] if row else default
    except Exception as e:
        print(f"Database fetch setting error: {e}")
        return default
    finally:
        conn.close()

def get_active_users(channel, minutes=1440):
    """Get a list of users who have been active in a channel recently"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # In a real app we'd use datetime objects, but our 'timestamp' is HH:MM:SS
        # For simplicity in this TUI, we'll just return unique users in the total history of the channel
        cursor.execute('''
            SELECT DISTINCT user FROM messages 
            WHERE channel = ? AND user != 'SYSTEM'
        ''', (channel,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Database active users error: {e}")
        return []
    finally:
        conn.close()

# Initialize on import
init_db()
