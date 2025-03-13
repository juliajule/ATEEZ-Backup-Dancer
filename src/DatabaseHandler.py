import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jobs.db")

def insertJobLog(job_name, job_type, start_time, end_time, files_copied, total_size, errors):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO job_logs (job_name, job_type, start_time, end_time, files_copied, total_size, errors)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (job_name, job_type, start_time, end_time, files_copied, total_size, errors))

    conn.commit()
    conn.close()

def getAllJobs(limit=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT id, job_name, job_type, start_time, end_time, files_copied, total_size, errors
        FROM job_logs
        WHERE DATE(start_time) = ?
        ORDER BY start_time DESC
    """, (today,))
    todays_jobs = cursor.fetchall()

    cursor.execute("""
        SELECT id, job_name, job_type, start_time, end_time, files_copied, total_size, errors
        FROM job_logs
        WHERE DATE(start_time) < ?
        ORDER BY start_time DESC
        LIMIT ?
    """, (today, limit))
    past_jobs = cursor.fetchall()

    conn.close()

    return todays_jobs, past_jobs