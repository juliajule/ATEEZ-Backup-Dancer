import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jobs.db")

def insertJobLog(job_name, job_type, start_time, end_time, files_copied, total_size, target_folder_size, transfer_speed, errors):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO job_logs (job_name, job_type, start_time, end_time, files_copied, total_size, target_folder_size, transfer_speed, errors)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (job_name, job_type, start_time, end_time, files_copied, total_size, target_folder_size, transfer_speed, errors,))

    conn.commit()
    conn.close()

def getAllJobs(limit=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

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

    return todays_jobs, past_jobs

def getLastSnapshot():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT end_time FROM job_logs WHERE job_type = 'snapshot' ORDER BY end_time DESC LIMIT 1
    """)
    last_snapshot = cursor.fetchone()
    conn.close()
    return datetime.fromisoformat(last_snapshot[0]) if last_snapshot else None
