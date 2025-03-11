import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_name TEXT,
        job_type TEXT,
        start_time TEXT,
        end_time TEXT,
        files_copied INTEGER,
        total_size INTEGER,
        errors TEXT
    )
    ''')

    conn.commit()
    conn.close()
    print(f"Datenbank erfolgreich erstellt unter: {DB_PATH}")

initialize_database()