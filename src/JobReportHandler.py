from src.BackUpHelper import *
from src.DatabaseHandler import getAllJobs
from src.Helpers import outputPrint
from datetime import datetime

def generateHtml(job):
    html_file = getJobInfo(job, "MAIN", "path")

    current_jobs, recent_jobs = getAllJobs()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Backup Jobs Übersicht</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <h1>Backup Jobs Übersicht</h1>
        <h2>Jobs vom {datetime.now().strftime('%d.%m.%Y')}</h2>
        <table>
            <tr>
                <th>Name</th>
                <th>Typ</th>
                <th>Startzeit</th>
                <th>Endzeit</th>
                <th>Dauer</th>
                <th>Dateien</th>
                <th>Total transferred file size</th>
                <th>Total File Size</th>
                <th>Geschwindigkeit</th>
                <th>Status</th>
            </tr>
    """

    for job in current_jobs:
        job_id, name, job_type, start, end, file_count, size, target_folder_size, transfer_speed, error = job
        duration = formatDuration(start, end)
        speed = calculateSpeed(size, start, end, transfer_speed) if end else "-"
        status_text = "" if not error else f"Fehler: {error}"
        status_icon = "success.png" if error is None else "error.png"
        size_display = f"{size / 1024 / 1024 / 1024:.2f} GB" if size >= 1024 * 1024 * 1024 else f"{size / 1024 / 1024:.2f} MB"
        target_folder_size_display = f"{target_folder_size / 1024 / 1024 / 1024:.2f} GB" if target_folder_size >= 1024 * 1024 * 1024 else f"{target_folder_size / 1024 / 1024:.2f} MB"

        html_content += f"""
            <tr>
                <td>{name.split('-')[-1].replace('.job', '')}</td>
                <td>{job_type}</td>
                <td>{start}</td>
                <td>{end if end else '- '}</td>
                <td>{duration}</td>
                <td>{file_count}</td>
                <td>{size_display}</td>
                <td>{target_folder_size_display}</td>
                <td>{speed}</td>
                <td><img src='{status_icon}' class="status-icon" alt='Status'> {status_text}</td>
            </tr>
        """

    html_content += """
        </table>
        <h2>Vergangene Jobs</h2>
        <table>
            <tr>
                <th>Name</th>
                <th>Typ</th>
                <th>Startzeit</th>
                <th>Endzeit</th>
                <th>Dauer</th>
                <th>Dateien</th>
                <th>Total transferred file size</th>
                <th>Total File Size</th>
                <th>Geschwindigkeit</th>
                <th>Status</th>
            </tr>
    """

    for job in recent_jobs:
        job_id, name, job_type, start, end, file_count, size, target_folder_size, transfer_speed, error = job
        duration = formatDuration(start, end)
        speed = calculateSpeed(size, start, end, transfer_speed) if end else "-"
        status_text = "" if not error else f"Fehler: {error}"
        status_icon = "success.png" if error is None else "error.png"
        size_display = f"{size / 1024 / 1024 / 1024:.2f} GB" if size >= 1024 * 1024 * 1024 else f"{size / 1024 / 1024:.2f} MB"
        target_folder_size_display = f"{target_folder_size / 1024 / 1024 / 1024:.2f} GB" if target_folder_size >= 1024 * 1024 * 1024 else f"{target_folder_size / 1024 / 1024:.2f} MB"

        html_content += f"""
            <tr>
                <td>{name.split('-')[-1].replace('.job', '')}</td>
                <td>{job_type}</td>
                <td>{start}</td>
                <td>{end}</td>
                <td>{duration}</td>
                <td>{file_count}</td>
                <td>{size_display}</td>
                <td>{target_folder_size_display}</td>
                <td>{speed}</td>
                <td><img src='{status_icon}' class="status-icon" alt='Status'> {status_text}</td>
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

def calculateSpeed(size, start, end, transfer_speed):
    try:
        if transfer_speed == 0:
            start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            duration = (end_dt - start_dt).total_seconds()
            return f"{(size / duration / 1024 / 1024):.2f} MB/s" if duration > 0 else "-"
        else:
            return f"{(transfer_speed / 1024 / 1024):.2f} MB/s"
    except:
        return "-"

def formatDuration(start, end):
    if not end:
        return "-"

    duration_seconds = (datetime.strptime(end, "%Y-%m-%d %H:%M:%S") - datetime.strptime(start, "%Y-%m-%d %H:%M:%S")).total_seconds()

    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    seconds = int(duration_seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"