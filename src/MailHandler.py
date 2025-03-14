import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.Helpers import *
from src.JobReportHandler import *


def mailJob(job):

    smtpServer = getJobInfo(job, "SMTP", "Server")
    smtpPort = getJobInfo(job, "SMTP", "Port")
    smtpUser = getJobInfo(job, "SMTP", "User")
    smtpPassword = getJobInfo(job, "SMTP", "Password")
    mailSender = getJobInfo(job, "MAIL", "Sender")
    mailRecipient = getJobInfo(job, "MAIL", "Recipient")

    hostname = socket.gethostname()
    todays_jobs, _ = getAllJobs()

    subject = f"Back Up {datetime.now().strftime('%Y-%m-%d')}"
    if any(job[9] for job in todays_jobs):
        subject += " - Error"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Backup Jobs Übersicht</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f4f4f4; }}
            .status-icon {{ height: 16px; width: 16px; }}
        </style>
    </head>
    <body>
        <h1>Backup Jobs Übersicht</h1>
        <h2>Jobs vom {datetime.now().strftime('%d.%m.%Y')}</h2>
        <p>Hostname: {hostname}</p>
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

    for job in todays_jobs:
        job_id, name, job_type, start, end, file_count, size, target_folder_size, transfer_speed, error = job
        duration = formatDuration(start, end)
        speed = calculateSpeed(size, start, end, transfer_speed) if end else "-"
        status_text = "Success" if not error else f"Fehler: {error}"
        status_icon = "✅" if error is None else "❌"
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
                <td>{speed}</td>
                <td>{target_folder_size_display}</td>
                <td>{status_icon} {status_text}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """


    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = mailSender
    msg["To"] = mailRecipient

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(smtpServer, smtpPort) as server:
            server.starttls()
            server.login(smtpUser, smtpPassword)
            server.sendmail(mailSender, mailRecipient, msg.as_string())

        outputPrint("E-Mail erfolgreich gesendet!")

    except Exception as e:
        outputPrint(f"Fehler beim Senden der E-Mail: {e}")

