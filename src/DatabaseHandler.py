import sqlite3
import os
from datetime import datetime
from src.Helpers import debug_print

# Define the database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jobs.db")

def insert_job_log(job_name, job_type, start_time, end_time, files_copied, total_size, target_folder_size, transfer_speed, errors):
    """
    Inserts a new job log entry into the database.
    """
    debug_print(f"Inserting job log: {job_name} ({job_type}) - {start_time} to {end_time}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO job_logs (job_name, job_type, start_time, end_time, files_copied, total_size, target_folder_size, transfer_speed, errors)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (job_name, job_type, start_time, end_time, files_copied, total_size, target_folder_size, transfer_speed, errors,))

    conn.commit()
    conn.close()
    debug_print("Job log successfully inserted.")


def get_all_jobs(limit=20):
    """
    Retrieves today's jobs and the last 'limit' number of past jobs from the database.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    debug_print(f"Fetching job logs for {today} and last {limit} past jobs")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, job_name, job_type, start_time, end_time, files_copied, total_size, target_folder_size, transfer_speed, errors
        FROM job_logs
        WHERE DATE(start_time) = ?
        ORDER BY start_time DESC
    """, (today,))
    todays_jobs = cursor.fetchall()

    cursor.execute("""
        SELECT id, job_name, job_type, start_time, end_time, files_copied, total_size, target_folder_size, transfer_speed, errors
        FROM job_logs
        WHERE DATE(start_time) < ?
        ORDER BY start_time DESC
        LIMIT ?
    """, (today, limit))
    past_jobs = cursor.fetchall()

    conn.close()
    debug_print(f"Retrieved {len(todays_jobs)} jobs for today and {len(past_jobs)} past jobs.")

    return todays_jobs, past_jobs

def get_last_snapshot():
    """
    Retrieves the end time of the last recorded snapshot job.
    """
    debug_print("Fetching last snapshot job.")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT end_time FROM job_logs WHERE job_type = 'snapshot' ORDER BY end_time DESC LIMIT 1
    """)
    last_snapshot = cursor.fetchone()
    conn.close()

    if last_snapshot:
        debug_print(f"Last snapshot job found: {last_snapshot[0]}")
        return datetime.fromisoformat(last_snapshot[0])
    else:
        debug_print("No snapshot job found.")
        return None