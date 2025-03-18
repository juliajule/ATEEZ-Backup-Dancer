from src.BackUpHelper import *
from src.Helpers import *
from src.ConfigHandler import *
from src.DatabaseHandler import insert_job_log
import subprocess
from io import StringIO
import re
import datetime

def sftp_job(job):
    """
    Handles an SFTP job using SCP for file transfers.
    """
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Retrieve SFTP binary path from config
    sftp = get_config("DEPENDENCIES", "sftp")
    debug_print(f"SFTP path: {sftp}")
    check_path_valid(sftp) or exit_on_error("SFTP path in config does not exist")

    # Source details
    source_remote = string_to_bool(get_job_info(job, "SOURCE", "remote")) or False
    source_hostname = get_job_info(job, "SOURCE", "hostname")
    source_user = get_job_info(job, "SOURCE", "user")
    source_port = get_job_info(job, "SOURCE", "port") or "22"
    source_path = get_job_info(job, "SOURCE", "path")

    # Destination details
    destination_remote = string_to_bool(get_job_info(job, "DESTINATION", "remote")) or False
    destination_hostname = get_job_info(job, "DESTINATION", "hostname")
    destination_user = get_job_info(job, "DESTINATION", "user")
    destination_port = get_job_info(job, "DESTINATION", "port") or "22"
    destination_path = get_job_info(job, "DESTINATION", "path")

    # Check for unsupported configurations
    if source_remote and destination_remote:
        output_print("Error: Both SOURCE and DESTINATION are remote, which is not supported.")
        return
    if not source_remote and not destination_remote:
        output_print("Error: Both SOURCE and DESTINATION are remote, which is not supported.")
        return

    files_before = count_files(destination_path, destination_remote, destination_user, destination_hostname)

    # Construct SCP command
    scp_line = ["scp", "-r", "-v"]

    if source_remote:
        scp_line += ["-P", source_port]
    elif destination_remote:
        scp_line += ["-P", destination_port]

    source = f"{source_user}@{source_hostname}:{source_path}" if source_remote else source_path
    destination = f"{destination_user}@{destination_hostname}:{destination_path}" if destination_remote else destination_path

    scp_line += [source, destination]
    output_print(f"Executing command: {' '.join(scp_line)}")

    full_output = StringIO()
    copied_files, total_size, transfer_speed = 0, 0, 0

    # Execute SCP command
    process = subprocess.Popen(
        scp_line,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    for line in process.stderr:
        if not line.strip():
            continue
        if "debug1" in line: # Ignore SSH debug messages
            continue

        output_print(line.strip())
        full_output.write(line)

        # Count transferred files
        if re.search(r"100%\s+\d+\s+\S+/\S+", line):
            copied_files += 1

        # Extract transferred bytes
        size_match = re.search(r"Transferred: sent (\d+), received (\d+) bytes", line)
        if size_match:
            sent_bytes = int(size_match.group(1))
            received_bytes = int(size_match.group(2))
            total_size = sent_bytes if source_remote else received_bytes

        # Extract transfer speed
        speed_match = re.search(r"Bytes per second: sent ([\d.]+), received ([\d.]+)", line)
        if speed_match:
            sent_speed = float(speed_match.group(1))
            received_speed = float(speed_match.group(2))
            transfer_speed = sent_speed if source_remote else received_speed

    process.stdout.close()
    returncode = process.wait()

    # Count files after transfer
    files_after = count_files(destination_path, destination_remote, destination_user, destination_hostname)
    copied_files = max(0, files_after - files_before)

    # Get destination folder size
    target_folder_size = get_folder_size(destination_path, destination_remote, destination_user, destination_hostname) if destination_remote else get_folder_size(destination_path)
    target_folder_size = target_folder_size or 0

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if returncode == 0:
        output_print("SFTP (via SCP) completed successfully.")
        error_message = None
    else:
        error_message = f"SFTP job failed with exit code {returncode}."
        output_print(error_message)

    # Log job in database
    insert_job_log(job, "sftp", start_time, end_time, copied_files, total_size, target_folder_size, transfer_speed, error_message)

def count_files(path, remote=False, ssh_user=None, ssh_host=None):
    """
    Counts the number of files in a directory, locally or remotely via SSH.
    """
    try:
        if remote:
            cmd = ["ssh", f"{ssh_user}@{ssh_host}", f'find "{path}" -type f | wc -l']
        else:
            cmd = ["sh", "-c", f'find "{path}" -type f | wc -l']

        result = subprocess.run(cmd, capture_output=True, text=True)

        return int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
    except Exception as e:
        output_print(f"Error counting files: {e}")
        return 0