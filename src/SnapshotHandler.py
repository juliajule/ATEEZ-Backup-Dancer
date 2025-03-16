from src.BackUpHelper import *
from src.Helpers import *
from src.DatabaseHandler import *
from src.ConfigHandler import *
import subprocess
import os
import datetime

def snapshotJob(job):

    zip = getConfig("REQUIREMENT", "7z")
    debugPrint(f"7zip: {zip}")
    checkPathValid(zip) or exitOnError("rsync Path in Config does not exist")

    hardLimit = int(getJobInfo(job, "MAIN", "Hard-Limit"))
    softLimit = int(getJobInfo(job, "MAIN", "Soft-Limit"))
    compressionLevel = getJobInfo(job, "MAIN", "Compression-Level")
    password = getJobInfo(job, "MAIN", "Zip-Password")
    sourcePath = getJobInfo(job, "MAIN", "source")
    destinationPath = getJobInfo(job, "MAIN", "destination")

    outputPrint(f"Snapshot-Job gestartet für {sourcePath} -> {destinationPath}")

    last_snapshot = getLastSnapshot()
    if last_snapshot and (datetime.datetime.now() - last_snapshot).days < softLimit:
        outputPrint(f"Letzter Snapshot ist nur {(datetime.datetime.now() - last_snapshot).days} Tage alt. Abbruch.")
        return

    start_time = datetime.datetime.now()
    snapshot_filename = f"Snapshot_{start_time.strftime('%Y-%m-%d')}.7z"
    snapshot_path = os.path.join(destinationPath, snapshot_filename)

    command = [
        "7z", "a", snapshot_path, sourcePath,
        f"-mx={compressionLevel}", f"-p{password}"
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        outputPrint(f"Snapshot erfolgreich erstellt: {snapshot_filename}")
    except subprocess.CalledProcessError as e:
        outputPrint(f"Fehler beim Erstellen des Snapshots: {e}")
        insertJobLog(job, "snapshot", start_time, datetime.datetime.now(), 0, 0, 0,0,e)
        return

    snapshots = sorted([
        f for f in os.listdir(destinationPath) if f.startswith("Snapshot_") and f.endswith(".7z")
    ], key=lambda f: os.path.getmtime(os.path.join(destinationPath, f)))

    while len(snapshots) > 2:
        file_to_remove = snapshots.pop(0)  # Älteste Datei außer den letzten beiden
        os.remove(os.path.join(destinationPath, file_to_remove))
        outputPrint(f"Mittlere Snapshot-Datei gelöscht: {file_to_remove}")

    if snapshots:
        oldest_snapshot = snapshots[0]
        file_path = os.path.join(destinationPath, oldest_snapshot)
        file_age = (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(file_path))).days

        if file_age > hardLimit:
            os.remove(file_path)
            outputPrint(f"Ältester Snapshot gelöscht, da älter als {hardLimit} Tage: {oldest_snapshot}")

    end_time = datetime.datetime.now()
    insertJobLog(job, "snapshot", start_time, end_time, 0, 0, 0,0,None)

    outputPrint("Snapshot-Job abgeschlossen.")