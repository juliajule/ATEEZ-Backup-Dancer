from src.BackUpHelper import *
from src.Helpers import *
from src.ConfigHandler import *
from src.DatabaseHandler import insertJobLog
import subprocess
from io import StringIO
import re
import datetime

def sftpJob(job):
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sftp = getConfig("REQUIREMENT", "sftp")
    debugPrint(f"sftp: {sftp}")
    checkPathValid(sftp) or exitOnError("sftp Path in Config does not exist")

    jobSourceRemote = stringToBool(getJobInfo(job, "SOURCE", "remote"))
    jobSourceHostname = getJobInfo(job, "SOURCE", "Hostname")
    jobSourceUser = getJobInfo(job, "SOURCE", "user")
    jobSourcePort = getJobInfo(job, "SOURCE", "Port")
    jobSourcePath = getJobInfo(job, "SOURCE", "Path")
    jobDestinationRemote = stringToBool(getJobInfo(job, "DESTINATION", "remote"))
    jobDestinationHostname = getJobInfo(job, "DESTINATION", "Hostname")
    jobDestinationUser = getJobInfo(job, "DESTINATION", "user")
    jobDestinationPort = getJobInfo(job, "DESTINATION", "Port")
    jobDestinationPath = getJobInfo(job, "DESTINATION", "Path")

    if jobSourceRemote and jobDestinationRemote:
        outputPrint("Error: Both SOURCE and DESTINATION are remote, which is not supported.")
        return

    files_before = countFiles(jobDestinationPath, remote=jobDestinationRemote,
                               ssh_user=jobDestinationUser, ssh_host=jobDestinationHostname)
    scpLine = ["scp", "-r", "-v"]

    if jobSourceRemote:
        scpLine += ["-P", jobSourcePort]
    elif jobDestinationRemote:
        scpLine += ["-P", jobDestinationPort]

    if jobSourceRemote:
        source = f"{jobSourceUser}@{jobSourceHostname}:{jobSourcePath}"
    else:
        source = jobSourcePath

    if jobDestinationRemote:
        destination = f"{jobDestinationUser}@{jobDestinationHostname}:{jobDestinationPath}"
    else:
        destination = jobDestinationPath

    scpLine += [source, destination]

    outputPrint(f"Running: {' '.join(scpLine)}")

    full_output = StringIO()
    copied_files = 0
    total_size = 0
    transfer_speed = 0

    process = subprocess.Popen(
        scpLine,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    for line in process.stderr:
        if not line.strip():
            continue
        if "debug1" in line:
            continue

        outputPrint(line.strip())
        full_output.write(line)

        if re.search(r"100%\s+\d+\s+\S+/\S+", line):
            copied_files += 1

        size_match = re.search(r"Transferred: sent (\d+), received (\d+) bytes", line)
        if size_match:
            sent_bytes = int(size_match.group(1))
            received_bytes = int(size_match.group(2))
            total_size = sent_bytes if jobSourceRemote else received_bytes

        speed_match = re.search(r"Bytes per second: sent ([\d.]+), received ([\d.]+)", line)
        if speed_match:
            sent_speed = float(speed_match.group(1))
            received_speed = float(speed_match.group(2))
            transfer_speed = sent_speed if jobSourceRemote else received_speed  # Wähle je nach Richtung

    process.stdout.close()
    returncode = process.wait()

    files_after = countFiles(jobDestinationPath, remote=jobDestinationRemote,
                              ssh_user=jobDestinationUser, ssh_host=jobDestinationHostname)

    copied_files = max(0, files_after - files_before)

    target_folder_size = getFolderSize(jobDestinationPath) or 0

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if returncode == 0:
        outputPrint("SFTP (via SCP) succeeded.")
        error_message = None
    else:
        error_message = f"Error with Code {returncode}."
        outputPrint(error_message)

    insertJobLog(job, "sftp", start_time, end_time, copied_files, total_size, target_folder_size, transfer_speed, error_message)

def countFiles(path, remote=False, ssh_user=None, ssh_host=None):
    try:
        if remote:
            cmd = ["ssh", f"{ssh_user}@{ssh_host}", f'find "{path}" -type f | wc -l']
        else:
            cmd = ["sh", "-c", f'find "{path}" -type f | wc -l']

        result = subprocess.run(cmd, capture_output=True, text=True)

        return int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
    except Exception as e:
        outputPrint(f"Fehler beim Zählen der Dateien: {e}")
        return 0