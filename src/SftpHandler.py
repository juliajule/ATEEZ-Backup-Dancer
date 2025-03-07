from src.BackUpHelper import *
from src.Helpers import *
from src.ConfigHandler import *
import subprocess
from io import StringIO

def sftpJob (job):

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

    scpLine = ["scp", "-r"]

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

    process = subprocess.Popen(
        scpLine,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        outputPrint(line.strip())
        full_output.write(line)

    process.stdout.close()
    returncode = process.wait()

    if returncode == 0:
        outputPrint("SFTP (via SCP) succeeded.")
    else:
        outputPrint(f"Error with Code {returncode}.")

    outputPrint("\n===== Full SCP Output =====")
    outputPrint(full_output.getvalue())