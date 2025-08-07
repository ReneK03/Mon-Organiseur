# modules/agenda_db.py
import sqlite3
import os

DB_PATH = "data/agenda.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            title TEXT,
            tag TEXT,
            color TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_event(date_str, title, tag=None, color=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO events (date, title, tag, color) VALUES (?, ?, ?, ?)",
              (date_str, title, tag, color))
    conn.commit()
    conn.close()

def get_events(date_str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, tag, color FROM events WHERE date = ?", (date_str,))
    rows = c.fetchall()
    conn.close()
    return rows

def update_event(event_id, new_title, new_tag=None, new_color=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE events SET title = ?, tag = ?, color = ? WHERE id = ?",
              (new_title, new_tag, new_color, event_id))
    conn.commit()
    conn.close()

def delete_event(event_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
