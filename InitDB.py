import sqlite3
import os

# Define database path
DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

def initialize_database():
    """Initializes the database and creates the job_logs table if it does not exist."""
    print(f"Initializing database at: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create job_logs table if it does not exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_name TEXT,
        job_type TEXT,
        start_time TEXT,
        end_time TEXT,
        files_copied INTEGER,
        total_size INTEGER,
        target_folder_size INTEGER,
        transfer_speed INTEGER,
        errors TEXT
    )
    ''')

    conn.commit()
    conn.close()
    print(f"Database successfully created at: {DB_PATH}")

initialize_database()