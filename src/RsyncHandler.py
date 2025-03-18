from src.BackUpHelper import *
from src.Helpers import *
from src.ConfigHandler import *
from src.DatabaseHandler import insert_job_log
import subprocess
import shlex
import datetime
import re

# List of arguments that should not be used in rsync jobs
FORBIDDEN_ARGUMENTS = ["--remove-source-files", "--recursive"]

def rsync_job(job):
    """
    Executes an rsync job based on the provided job configuration.
    """
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rsync = get_config("DEPENDENCIES", "rsync")
    debug_print(f"Using rsync binary: {rsync}")
    check_path_valid(rsync) or exit_on_error("Rsync path in configuration does not exist")

    # Retrieve job-specific settings
    delete_on_destination = get_job_info(job, "RSYNC_SETTINGS", "deleteOnDestination")
    standard_arguments = get_job_info(job, "RSYNC_SETTINGS", "standardArguments") or ""
    excluded_directories = get_job_info(job, "RSYNC_SETTINGS", "excludeDirectories")

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

    # Validate job configuration
    standard_arguments = validate_job_config(delete_on_destination, standard_arguments, source_remote, destination_remote, source_hostname, source_user, destination_hostname, destination_user)

    if standard_arguments == "Fail":
        debug_print("Job configuration failed. Job aborted.")
        insert_job_log(job, "rsync", start_time, None, 0, 0, 0, 0, "Job configuration failed")
        return

    # Construct rsync command
    rsync_line = ["rsync", "--stats"]

    if standard_arguments:
        rsync_line += standard_arguments

    if delete_on_destination:
        rsync_line.append("--delete")

    if excluded_directories and excluded_directories.lower() != "none":
        for directory in excluded_directories.split(","):
            directory = directory.strip()
            if directory:
                rsync_line.append(f"--exclude={directory}")

    # Handle remote source/destination
    if source_hostname and source_remote:
        source = f"{source_user}@{source_hostname}:{source_path}"
        rsync_line += ["-e", f"ssh -p {source_port}", source, destination_path]
    if destination_hostname and destination_remote:
        destination = f"{destination_user}@{destination_hostname}:{destination_path}"
        rsync_line += ["-e", f"ssh -p {destination_port}", source_path, destination]
    if not (source_remote or destination_remote):
        rsync_line += [source_path, destination_path]

    output_print(f"Executing: {' '.join(rsync_line)}")

    # Execute rsync command
    process = subprocess.Popen(
        rsync_line,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
    )

    copied_files, total_size, target_folder_size, transfer_speed = 0, 0, 0, 0

    for line in process.stdout:
        output_print(line.strip())

        # Extract transferred files
        match_files = re.search(r"Number of files transferred:\s+(\d+)", line)
        if match_files:
            copied_files = int(match_files.group(1))

        # Extract transferred bytes
        match_size = re.search(r"Total transferred file size:\s+([\d,]+) bytes", line)
        if match_size:
            total_size = int(match_size.group(1).replace(",", ""))

        # Extract destination folder size
        match_files = re.search(r"Total file size:\s+(\d+)", line)
        if match_files:
            target_folder_size = int(match_files.group(1))

        # Extract transfer speed
        match_speed = re.search(r"([\d,.]+) bytes/sec", line)
        if match_speed:
            transfer_speed = float(match_speed.group(1).replace(".", "").replace(",", "."))

    process.stdout.close()
    returncode = process.wait()
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log job outcome
    if returncode == 0:
        output_print("Rsync completed successfully.")
        insert_job_log(job, "rsync", start_time, end_time, copied_files, total_size, target_folder_size, transfer_speed, None)
    else:
        error_message = f"Error: Rsync failed with exit code {returncode}."
        output_print(error_message)
        insert_job_log(job, "rsync", start_time, end_time, copied_files, total_size, target_folder_size, transfer_speed, error_message)


def validate_job_config(delete_on_destination, standard_arguments, source_remote, destination_remote, source_hostname, source_user, destination_hostname, destination_user):
    """
    Validates the job configuration and removes forbidden arguments if necessary.
    """
    if source_remote and destination_remote:
        debug_print(f"{source_remote} -> {destination_remote}")
        output_print("Error: Both source and destination are remote, which is not supported.")
        return "Fail"

    if source_remote:
        if not source_hostname or not source_user:
            output_print("Error: SOURCE is remote, but hostname or user is missing.")
            return "Fail"

    if destination_remote:
        if not destination_hostname or not destination_user:
            output_print("Error: DESTINATION is remote, but hostname or user is missing.")
            return "Fail"

    args_list = shlex.split(standard_arguments) or ""
    cleaned_args = []

    for arg in args_list:
        if arg in FORBIDDEN_ARGUMENTS:
            output_print(f"Warning: Forbidden argument '{arg}' removed from standard arguments.")
        else:
            cleaned_args.append(arg)

    if delete_on_destination and "--delete" in args_list:
        debug_print("Warning: '--delete' removed from standard arguments since DeleteOnDestination is set to true.")
        cleaned_args = [arg for arg in args_list if arg != "--delete"]

    output_print("Job configuration validated successfully.")
    return cleaned_args