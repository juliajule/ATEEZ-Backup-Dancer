import sqlite3
import os

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

    cursor.execute("""
        SELECT id, job_name, job_type, start_time, end_time, files_copied, total_size, errors
        FROM job_logs
        WHERE end_time IS NULL OR end_time = (SELECT MAX(end_time) FROM job_logs WHERE end_time IS NOT NULL)
        ORDER BY start_time DESC
    """)
    current_and_last_jobs = cursor.fetchall()

    cursor.execute("""
        SELECT id, job_name, job_type, start_time, end_time, files_copied, total_size, errors
        FROM job_logs
        WHERE end_time IS NOT NULL
        ORDER BY end_time DESC
        LIMIT ?
    """, (limit,))
    recent_jobs = cursor.fetchall()

    conn.close()

    return current_and_last_jobs, recent_jobs