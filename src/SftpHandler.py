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
    check_path_valid(sftp) or exitOnError("sftp Path in Config does not exist")

    jobSourceRemote = str_to_bool(getJobInfo(job, "SOURCE", "remote"))
    jobSourceHostname = getJobInfo(job, "SOURCE", "Hostname")
    jobSourceUser = getJobInfo(job, "SOURCE", "user")
    jobSourcePort = getJobInfo(job, "SOURCE", "Port")
    jobSourcePath = getJobInfo(job, "SOURCE", "Path")
    jobDestinationRemote = str_to_bool(getJobInfo(job, "DESTINATION", "remote"))
    jobDestinationHostname = getJobInfo(job, "DESTINATION", "Hostname")
    jobDestinationUser = getJobInfo(job, "DESTINATION", "user")
    jobDestinationPort = getJobInfo(job, "DESTINATION", "Port")
    jobDestinationPath = getJobInfo(job, "DESTINATION", "Path")

    if jobSourceRemote and jobDestinationRemote:
        outputPrint("Error: Both SOURCE and DESTINATION are remote, which is not supported.")
        return

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

    process = subprocess.Popen(
        scpLine,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        if not line.strip():
            continue
        if "debug1" in line:
            continue

        outputPrint(line.strip())
        full_output.write(line)

# Geht noch nicht korrekt
        if re.search(r"^.*->.*", line):
            copied_files += 1
        size_match = re.search(r"\((\d+) bytes\)", line)
        if size_match:
            total_size += int(size_match.group(1))

    process.stdout.close()
    returncode = process.wait()

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if returncode == 0:
        outputPrint("SFTP (via SCP) succeeded.")
        error_message = None
    else:
        error_message = f"Error with Code {returncode}."
        outputPrint(error_message)

    insertJobLog(
        job_name=job,
        job_type="sftp",
        start_time=start_time,
        end_time=end_time,
        files_copied=copied_files,
        total_size=total_size,
        errors=error_message
    )