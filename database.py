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

# Initialize on import
init_db()
