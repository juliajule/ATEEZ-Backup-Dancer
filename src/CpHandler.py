from src.BackUpHelper import *
from src.Helpers import *
from src.DatabaseHandler import insertJobLog
import os
import shutil
import datetime

def cpJob(job):
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    jobSource = getJobInfo(job, "MAIN", "source")
    jobDestination = getJobInfo(job, "MAIN", "destination")
    onDuplicates = getJobInfo(job, "MAIN", "onDuplicate")

    if not os.path.exists(jobSource):
        error_message = f"Fehler: Quellpfad '{jobSource}' existiert nicht."
        outputPrint(error_message)
        insertJobLog(job, "copy", start_time, None, 0, 0, 0, 0, error_message)
        return

    if not os.path.exists(jobDestination):
        error_message = f"Fehler: Zielpfad '{jobDestination}' existiert nicht."
        outputPrint(error_message)
        insertJobLog(job, "copy", start_time, None, 0, 0, 0, 0, error_message)
        return

    outputPrint(f"Starte Kopiervorgang von {jobSource} nach {jobDestination}")

    copied_files = 0
    total_size = 0
    target_folder_size = 0
    transfer_speed = 0

    for root, _, files in os.walk(jobSource):
        rel_path = os.path.relpath(root, jobSource)
        dest_dir = os.path.join(jobDestination, rel_path)

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, file)

            if os.path.exists(dest_file):
                if onDuplicates == "skip":
                    outputPrint(f"Überspringe doppelte Datei: {dest_file}")
                    continue
                elif onDuplicates == "backup":
                    backup_file = dest_file + ".bak"
                    outputPrint(f"Backup von {dest_file} nach {backup_file}")
                    shutil.move(dest_file, backup_file)
                elif onDuplicates == "overwrite":
                    outputPrint(f"Überschreibe Datei: {dest_file}")
                else:
                    error_message = f"Unbekannte OnDuplicate-Option: {onDuplicates}"
                    outputPrint(error_message)
                    insertJobLog(job, "copy", start_time, None, copied_files, total_size, target_folder_size, transfer_speed, error_message)
                    return

            shutil.copy2(src_file, dest_file)
            copied_files += 1
            total_size += os.path.getsize(src_file)
            outputPrint(f"Kopiert: {src_file} → {dest_file}")

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    outputPrint("Kopiervorgang abgeschlossen.")

    insertJobLog(job, "copy", start_time, end_time, copied_files, total_size, target_folder_size, transfer_speed, None)