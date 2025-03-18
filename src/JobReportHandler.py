from src.BackUpHelper import *
from src.DatabaseHandler import get_all_jobs
from src.Helpers import output_print
from datetime import datetime

def generate_html(job):
    """
    Generates an HTML file displaying backup job information.
    """
    html_file = get_job_info(job, "OUTPUT", "path")
    current_jobs, recent_jobs = get_all_jobs()

    debug_print(f"Generating HTML report: {html_file}")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Backup Job Report</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <h1>Backup Job Overview</h1>
        <h2>Jobs from {datetime.now().strftime('%d.%m.%Y')}</h2>
        <table>
            <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Duration</th>
                <th>Files</th>
                <th>Transferred Size</th>
                <th>Total Size</th>
                <th>Speed</th>
                <th>Status</th>
            </tr>
    """
    for job in current_jobs:
        html_content += generate_html_row(job)

    html_content += """
        </table>
        <h2>Vergangene Jobs</h2>
        <table>
            <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Duration</th>
                <th>Files</th>
                <th>Transferred Size</th>
                <th>Total Size</th>
                <th>Speed</th>
                <th>Status</th>
            </tr>
    """

    for job in recent_jobs:
        html_content += generate_html_row(job)

    html_content += """
        </table>
    </body>
    </html>
    """

    with open(html_file, "w", encoding="utf-8") as file:
        file.write(html_content)

    output_print(f"HTML file successfully created: {html_file}")

def generate_html_row(job):
    """
    Generates a single row of the HTML table for a job.
    """
    job_id, name, job_type, start, end, file_count, size, target_folder_size, transfer_speed, error = job
    duration = format_duration(start, end)
    speed = calculate_speed(size, start, end, transfer_speed) if end else "-"
    status_text = "" if not error else f"Error: {error}"
    status_icon = "success.png" if error is None else "error.png"
    size_display = format_size(size)
    target_size_display = format_size(target_folder_size)

    return f"""
        <tr>
            <td>{name.split('-')[-1].replace('.job', '')}</td>
            <td>{job_type}</td>
            <td>{start}</td>
            <td>{end if end else '- '}</td>
            <td>{duration}</td>
            <td>{file_count}</td>
            <td>{size_display}</td>
            <td>{target_size_display}</td>
            <td>{speed}</td>
            <td><img src='{status_icon}' class="status-icon" alt='Status'> {status_text}</td>
        </tr>
    """

def format_size(size):
    """
    Formats file size in MB or GB for display.
    """
    if size >= 1024 * 1024 * 1024:
        return f"{size / 1024 / 1024 / 1024:.2f} GB"
    return f"{size / 1024 / 1024:.2f} MB"

def calculate_speed(size, start, end, transfer_speed):
    """
    Calculates the transfer speed in MB/s.
    """
    try:
        if transfer_speed == 0:
            start_dt = parse_datetime(start)
            end_dt = parse_datetime(end)
            duration = (end_dt - start_dt).total_seconds()
            return f"{(size / duration / 1024 / 1024):.2f} MB/s" if duration > 0 else "-"
        else:
            return f"{(transfer_speed / 1024 / 1024):.2f} MB/s"
    except Exception as e:
        debug_print(f"Error calculating speed: {e}")
        return "-"

def parse_datetime(timestamp):
    """
    Parses a timestamp, supporting both formats (with and without milliseconds).
    """
    try:
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")

def format_duration(start, end):
    """
    Formats job duration as h/m/s.
    """
    if not end:
        return "-"

    try:
        duration_seconds = (
                datetime.strptime(end.split(".")[0], "%Y-%m-%d %H:%M:%S") -
                datetime.strptime(start.split(".")[0], "%Y-%m-%d %H:%M:%S")
        ).total_seconds()

        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    except Exception as e:
        debug_print(f"Error formatting duration: {e}")
        return "-"