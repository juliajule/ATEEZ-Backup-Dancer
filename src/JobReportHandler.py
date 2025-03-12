import sqlite3
from src.BackUpHelper import *
from src.DatabaseHandler import getAllJobs
from src.Helpers import outputPrint


def generateHtml(job):
    html_file = getJobInfo(job, "MAIN", "path")

    current_jobs, recent_jobs = getAllJobs()

    html_content = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Backup Jobs Übersicht</title>
    </head>
    <body>
        <h1>Backup Jobs Übersicht</h1>
        <h2>Aktuelle Jobs</h2>
        <table>
            <tr>
                <th>Job Name</th>
                <th>Art</th>
                <th>Dauer</th>
                <th>Dateien</th>
                <th>Größe</th>
                <th>Status</th>
            </tr>
    """

    for job in current_jobs:
        job_id, job_name, job_type, start_time, end_time, file_count, total_size, error_message = job
        duration = "-" if not end_time else str(round((sqlite3.datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") - sqlite3.datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")).total_seconds() / 60, 2)) + " min"
        status_icon = "success.png" if error_message is None else "error.png"
        status_text = "Erfolgreich" if error_message is None else error_message

        html_content += f"""
            <tr>
                <td>{job_name}</td>
                <td>{job_type}</td>
                <td>{duration}</td>
                <td>{file_count}</td>
                <td>{total_size} KB</td>
                <td><img src='{status_icon}' alt='Status'> {status_text}</td>
            </tr>
        """

    html_content += """
        </table>
        <h2>Vergangene Jobs</h2>
        <table>
            <tr>
                <th>Job Name</th>
                <th>Art</th>
                <th>Dauer</th>
                <th>Dateien</th>
                <th>Größe</th>
                <th>Status</th>
            </tr>
    """

    for job in recent_jobs:
        job_id, job_name, job_type, start_time, end_time, file_count, total_size, error_message = job
        duration = "-" if not end_time else str(round((sqlite3.datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") - sqlite3.datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")).total_seconds() / 60, 2)) + " min"
        status_icon = "success.png" if error_message is None else "error.png"
        status_text = "Erfolgreich" if error_message is None else error_message

        html_content += f"""
            <tr>
                <td>{job_name}</td>
                <td>{job_type}</td>
                <td>{duration}</td>
                <td>{file_count}</td>
                <td>{total_size} KB</td>
                <td><img src='{status_icon}' alt='Status'> {status_text}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    with open(html_file, "w", encoding="utf-8") as file:
        file.write(html_content)

    outputPrint(f"HTML-Datei wurde erfolgreich erstellt: {html_file}")
