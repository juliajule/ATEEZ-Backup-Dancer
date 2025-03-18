from src.BackUpHelper import *
from src.Helpers import *
from src.DatabaseHandler import insert_job_log
import os
import shutil
import datetime

def cp_job(job):
    """
     Handles the file copy job based on the provided job configuration.
     Logs the process and records job details in the database.
     """
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Retrieve job details from configuration
    source = get_job_info(job, "SOURCE", "path")
    destination = get_job_info(job, "DESTINATION", "path")
    on_duplicates = get_job_info(job, "COPY_OPTIONS", "onDuplicate") or "overwrite"

    debug_print(f"Starting copy job: {job}")
    debug_print(f"Source: {source}")
    debug_print(f"Destination: {destination}")
    debug_print(f"OnDuplicate setting: {on_duplicates}")

    # Validate source and destination paths
    if not os.path.exists(source):
        error_message = f"Error: Source path '{source}' does not exist."
        output_print(error_message)
        insert_job_log(job, "copy", start_time, None, 0, 0, 0, 0, error_message)
        return

    if not os.path.exists(destination):
        error_message = f"Error: Destination path '{destination}' does not exist."
        output_print(error_message)
        insert_job_log(job, "copy", start_time, None, 0, 0, 0, 0, error_message)
        return

    output_print(f"Starting copy operation from {source} to {destination}")

    copied_files = 0
    total_size = 0
    transfer_speed = 0

    # Walk through the source directory
    for root, _, files in os.walk(source):
        rel_path = os.path.relpath(root, source)
        dest_dir = os.path.join(destination, rel_path)

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            debug_print(f"Created directory: {dest_dir}")

    for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, file)

            # Handle duplicate files based on 'on_duplicates' setting
            if os.path.exists(dest_file):
                if on_duplicates == "skip":
                    output_print(f"Skipping duplicate file: {dest_file}")
                    continue
                elif on_duplicates == "backup":
                    backup_file = dest_file + ".bak"
                    output_print(f"Creating backup: {dest_file} → {backup_file}")
                    shutil.move(dest_file, backup_file)
                elif on_duplicates == "overwrite":
                    output_print(f"Overwriting file: {dest_file}")
                else:
                    error_message = f"Unknown OnDuplicate option: {on_duplicates}"
                    output_print(error_message)
                    insert_job_log(job, "copy", start_time, None, copied_files, total_size, 0, transfer_speed, error_message)
                    return

            shutil.copy2(src_file, dest_file)
            copied_files += 1
            total_size += os.path.getsize(src_file)
            debug_print(f"Copied: {src_file} → {dest_file} ({total_size} bytes)")

    # Get final target folder size
    target_folder_size = get_folder_size(destination) or 0

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    output_print("Copy operation completed.")
    debug_print(f"Total files copied: {copied_files}")
    debug_print(f"Total size copied: {total_size} bytes")
    debug_print(f"Final target folder size: {target_folder_size} bytes")

    # Insert job details into the database
    insert_job_log(job, "copy", start_time, end_time, copied_files, total_size, target_folder_size, transfer_speed, None)