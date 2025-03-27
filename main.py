#!/usr/bin/env python

from src.RsyncHandler import *
from src.CpHandler import *
from src.SftpHandler import *
from src.MailHandler import *
from src.SnapshotHandler import *

version = 0.1

# Initialize configuration
config_check()
log_level = get_config("LOGGING", "logLevel") or "1"
debug_level = get_config("LOGGING", "debugLevel") or "0"
file_logging = get_config("LOGGING", "fileLogging") or "0"

# Set logging levels
initialize_logging(log_level, debug_level, file_logging)
debug_print("Config file found")
debug_print(f"Log level: {log_level} -- Debug level: {debug_level} -- File logging: {file_logging}")

# Welcome message
print(f"\n")
output_print(f"Welcome to ATEEZ Backup Dancer {version}")
output_print("Startet successfully")
output_print("\n----")

# Get all job files
jobs = get_job_list() or debug_print(f"Jobs directory does not exist or has no valid .job Files") & exit(0)
output_print(f"Found {len(jobs)} jobs:")
for job in jobs:
    output_print(f"{job}")
output_print("\n----")

# Process all jobs
for job_counter, job in enumerate(jobs, start=1):
    output_print(f"Start Job {job_counter} ({job})")

    job_type = get_job_info(job, "JOB_SETTINGS", "type")
    job_active = string_to_bool(get_job_info(job, "JOB_SETTINGS", "active"))

    output_print(f" Job Type:     {job_type}")

    if not job_active:
        output_print(f"Skipping {job_type} job")
        debug_print(f"{job_type} job is not activated in job file: {job}")
        output_print("\n----")
        continue

    # Execute job based on type
    job_functions = {
        "snapshot": snapshot_job,
        "rsync": rsync_job,
        "sftp": sftp_job,
        "cp": cp_job,
        "jobReport": generate_html,
        "mail": mail_job
    }

    if job_type in job_functions:
        job_functions[job_type](job)
    else:
        output_print(f"Unknown job type: {job_type}")
        debug_print(f"Skipping unknown job type in job file: {job}")

    output_print("\n----")

output_print("All done! Hopefully everything went well.")
output_print("Have a nice day, see you next time.")
output_print("And stream ATEEZ!")

rotate_logs()