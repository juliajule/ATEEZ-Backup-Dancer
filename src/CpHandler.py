from src.BackUpHelper import *
from src.Helpers import *
import os
import shutil

def cpJob(job):

    jobSource = getJobInfo(job, "MAIN", "source")
    jobDestination = getJobInfo(job, "MAIN", "destination")
    onDuplicates = getJobInfo(job, "MAIN", "onDuplicate")

    if not os.path.exists(jobSource):
        outputPrint(f"Fehler: Quellpfad '{jobSource}' existiert nicht.")
        return

    if not os.path.exists(jobDestination):
        outputPrint(f"Fehler: Zielpfad '{jobDestination}' existiert nicht.")
        return

    outputPrint(f"Starte Kopiervorgang von {jobSource} nach {jobDestination}")

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
                    outputPrint(f"Unbekannte OnDuplicate-Option: {onDuplicates}")
                    return

            shutil.copy2(src_file, dest_file)
            outputPrint(f"Kopiert: {src_file} → {dest_file}")

    outputPrint("Kopiervorgang abgeschlossen.")