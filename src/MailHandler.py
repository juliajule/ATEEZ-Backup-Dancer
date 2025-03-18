import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.Helpers import *
from src.JobReportHandler import *


def mail_job(job):
    """
    Sends an email report containing the backup job results.
    """
    debug_print("Starting mail job...")

    # Retrieve SMTP settings from job configuration
    smtp_server = get_job_info(job, "SMTP_SETTINGS", "server")
    smtp_port = get_job_info(job, "SMTP_SETTINGS", "port")
    smtp_user = get_job_info(job, "SMTP_SETTINGS", "user")
    smtp_password = get_job_info(job, "SMTP_SETTINGS", "password")
    mail_sender = get_job_info(job, "EMAIL_DETAILS", "sender")
    mail_recipient = get_job_info(job, "EMAIL_DETAILS", "recipient")

    debug_print(f"SMTP Server: {smtp_server}, Port: {smtp_port}")
    debug_print(f"Sender: {mail_sender}, Recipient: {mail_recipient}")

    hostname = socket.gethostname()
    todays_jobs, _ = get_all_jobs()

    # Construct email subject
    subject = f"Back Up {datetime.now().strftime('%Y-%m-%d')}"
    if any(job[9] for job in todays_jobs):
        subject += " - Error"
    debug_print(f"Email subject: {subject}")

    # Construct HTML email content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Backup Job Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <h1>Backup Job Report</h1>
        <h2>Jobs from {datetime.now().strftime('%d.%m.%Y')}</h2>
        <p>Hostname: {hostname}</p>
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

    for job in todays_jobs:
        job_id, name, job_type, start, end, file_count, size, target_folder_size, transfer_speed, error = job
        duration = format_duration(start, end)
        speed = calculate_speed(size, start, end, transfer_speed) if end else "-"
        status_text = "Success" if not error else f"Error: {error}"
        status_icon = "✅" if error is None else "❌"
        size_display = f"{size / 1024 / 1024 / 1024:.2f} GB" if size >= 1024 * 1024 * 1024 else f"{size / 1024 / 1024:.2f} MB"
        target_folder_size_display = f"{target_folder_size / 1024 / 1024 / 1024:.2f} GB" if target_folder_size >= 1024 * 1024 * 1024 else f"{target_folder_size / 1024 / 1024:.2f} MB"

        debug_print(f"Processing job: {name}, Status: {status_text}")

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

    # Create email message
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = mail_sender
    msg["To"] = mail_recipient
    msg.attach(MIMEText(html_content, "html"))

    debug_print("Attempting to send email...")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(mail_sender, mail_recipient, msg.as_string())
        output_print("Email sent successfully!")
    except Exception as e:
        output_print(f"Error sending email: {e}")
        debug_print(f"Exception: {e}")
