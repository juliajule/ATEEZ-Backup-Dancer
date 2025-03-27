from src.BackUpHelper import *
from src.Helpers import *
from src.DatabaseHandler import *
from src.ConfigHandler import *
import subprocess
import os
import datetime

def snapshot_job(job):
    """
    Creates a compressed snapshot of the specified source directory and manages snapshot retention.
    """
    start_time = datetime.datetime.now()
    debug_print(f"Starting snapshot job at {start_time}")

    # Load required configurations
    zip_path = get_config("DEPENDENCIES", "7z")
    debug_print(f"7-Zip path: {zip_path}")
    check_path_valid(zip_path) or exit_on_error("7-Zip path in config does not exist")

    # Retrieve job-specific settings
    hard_limit = int(get_job_info(job, "SNAPSHOT_SETTINGS", "hardLimit"))
    soft_limit = int(get_job_info(job, "SNAPSHOT_SETTINGS", "softLimit"))
    compression_level = get_job_info(job, "SNAPSHOT_SETTINGS", "compressionLevel") or "5"
    cores = get_job_info(job, "SNAPSHOT_SETTINGS", "cores") or "1"
    password = get_job_info(job, "SNAPSHOT_SETTINGS", "zipPassword") or "None"
    source_path = get_job_info(job, "SOURCE", "source")
    destination_path = get_job_info(job, "DESTINATION", "destination")

    debug_print(f"Configuration loaded: hard_limit={hard_limit}, soft_limit={soft_limit}, compression_level={compression_level}, password={'set' if password != 'None' else 'not set'}")
    debug_print(f"Source path: {source_path}, Destination path: {destination_path}")
    output_print(f"Snapshot-Job started: {source_path} -> {destination_path}")

    # Check last snapshot
    last_snapshot = get_last_snapshot()
    if last_snapshot:
        last_snapshot_age = (datetime.datetime.now() - last_snapshot).days
        debug_print(f"Last snapshot age: {last_snapshot_age} days")
        if last_snapshot_age < soft_limit:
            output_print(f"Last snapshot is only {last_snapshot_age} days old. Aborting snapshot job.")
            return

    # Generate snapshot file name and path
    snapshot_filename = f"Snapshot_{start_time.strftime('%Y-%m-%d')}.7z"
    snapshot_path = os.path.join(destination_path, snapshot_filename)
    debug_print(f"Generated snapshot file path: {snapshot_path}")

    # Construct 7-Zip command
    command = ["7z", "a", snapshot_path, source_path, f"-mx={compression_level}"]
    if password != "None":
        command += [f"-p{password}"]
    if cores.lower() != "all":
        command += [f"-mmt={cores}"]
    if cores.lower() == "all":
        command += [f"-mmt"]
    debug_print(f"Generated 7-Zip command: {' '.join(command)}")

    # Execute snapshot creation
    try:
        debug_print(f"Executing snapshot creation...")
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        output_print(f"Snapshot successfully created: {snapshot_filename}")
    except subprocess.CalledProcessError as e:
        output_print(f"Error during snapshot creation: {e}")
        insert_job_log(job, "snapshot", start_time, datetime.datetime.now(), 0, 0, 0, 0, e)
        return

    # Manage snapshot retention
    snapshots = sorted([
        f for f in os.listdir(destination_path) if f.startswith("Snapshot_") and f.endswith(".7z")
    ], key=lambda f: os.path.getmtime(os.path.join(destination_path, f)))
    debug_print(f"Existing snapshots found: {snapshots}")

    # Ensure only two snapshots are kept
    while len(snapshots) > 2:
        file_to_remove = snapshots.pop(0)  # Älteste Datei außer den letzten beiden
        os.remove(os.path.join(destination_path, file_to_remove))
        output_print(f"Removed excess snapshot: {file_to_remove}")

    # Remove outdated snapshots exceeding hard limit
    if snapshots:
        oldest_snapshot = snapshots[0]
        file_path = os.path.join(destination_path, oldest_snapshot)
        file_age = (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(file_path))).days
        debug_print(f"Oldest snapshot age: {file_age} days (limit: {hard_limit})")
        if file_age > hard_limit:
            os.remove(file_path)
            output_print(f"Deleted oldest snapshot due to exceeding {hard_limit} days: {oldest_snapshot}")

    end_time = datetime.datetime.now()
    insert_job_log(job, "snapshot", start_time, end_time, 0, 0, 0, 0, None)
    output_print("Snapshot job completed successfully.")