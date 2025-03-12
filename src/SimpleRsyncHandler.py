from src.BackUpHelper import *
from src.Helpers import *
from src.ConfigHandler import *
from src.DatabaseHandler import insertJobLog
import subprocess
import shlex
import datetime
import re

FORBIDDEN_ARGUMENTS = ["--remove-source-files", "--recursive"]

def rsyncJob(job):
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rsync = getConfig("REQUIREMENT", "rsync")
    debugPrint(f"rsync: {rsync}")
    check_path_valid(rsync) or exitOnError("rsync Path in Config does not exist")

    # Alle Informationen aus der Konfig
    jobDeleteOnDestination = getJobInfo(job, "MAIN", "DeleteOnDestination")
    jobStandardArguments = getJobInfo(job, "MAIN", "StandardArguments")
    jobSourceRemote = str_to_bool(getJobInfo(job, "SOURCE", "remote"))
    jobSourceHostname = getJobInfo(job, "SOURCE", "Hostname")
    jobSourceUser = getJobInfo(job, "SOURCE", "user")
    jobSourcePort = getJobInfo(job, "SOURCE", "Port")
    jobSourcePath = getJobInfo(job, "SOURCE", "Path")
    jobDestinationRemote = str_to_bool(getJobInfo(job, "DESTINATION", "remote"))
    jobDestinationHostname = getJobInfo(job, "DESTINATION", "Hostname")
    jobDestinationUser = getJobInfo(job, "DESTINATION", "user")
    jobDestinationPort = getJobInfo(job, "DESTINATION", "Port")
    jobDestionationPath = getJobInfo(job, "DESTINATION", "Path")

    #Logic Checks
    jobStandardArguments = validate_job_config(jobDeleteOnDestination, jobStandardArguments, jobSourceRemote, jobDestinationRemote, jobSourceHostname, jobSourceUser, jobDestinationHostname, jobDestinationUser)

    if jobStandardArguments == "Fail":
        insertJobLog(job, "rsync", start_time, None, 0, 0, "Job-Konfiguration fehlgeschlagen")
        return

    rsyncLine = ["rsync", "--stats"]

    if jobStandardArguments:
        rsyncLine += jobStandardArguments

    if jobDeleteOnDestination:
        rsyncLine.append("--delete")

    if jobSourceHostname and jobSourceRemote:
        source = f"{jobSourceUser}@{jobSourceHostname}:{jobSourcePath}"
        rsyncLine += [source, jobDestionationPath]

    if jobDestinationHostname and jobDestinationRemote:
        destination = f"{jobDestinationUser}@{jobDestinationHostname}:{jobDestionationPath}"
        rsyncLine += [jobSourcePath, destination]

    if not (jobSourceRemote or jobDestinationRemote):
        rsyncLine += [jobSourcePath, jobDestionationPath]

    outputPrint(f"Running: {rsyncLine}")

    process = subprocess.Popen(
        rsyncLine,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    copied_files = 0
    total_size = 0

    for line in process.stdout:
        outputPrint(line.strip())

        match_files = re.search(r"Number of files transferred:\s+(\d+)", line)
        if match_files:
            copied_files = int(match_files.group(1))

        match_size = re.search(r"Total file size:\s+([\d,]+) bytes", line)
        if match_size:
            total_size = int(match_size.group(1).replace(",", ""))

    process.stdout.close()
    returncode = process.wait()
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if returncode == 0:
        outputPrint("Rsync succeeded.")
        insertJobLog(job, "rsync", start_time, end_time, copied_files, total_size, None)
    else:
        error_message = f"Error with Code {returncode}."
        outputPrint(error_message)
        insertJobLog(job, "rsync", start_time, end_time, copied_files, total_size, error_message)


def validate_job_config(jobDeleteOnDestination, jobStandardArguments, jobSourceRemote, jobDestinationRemote, jobSourceHostname, jobSourceUser, jobDestinationHostname, jobDestinationUser):

    if jobSourceRemote and jobDestinationRemote:
        debugPrint(f"{jobSourceRemote} -> {jobDestinationRemote}")
        outputPrint("Error: Source and destination are both remote, Job ends")
        return

    args_list = shlex.split(jobStandardArguments) or ""

    cleaned_args = []
    for arg in args_list:
        if arg in FORBIDDEN_ARGUMENTS:
            outputPrint(f"Note: Forbidden argument '{arg}' has been removed from StandardArguments.")
        else:
            cleaned_args.append(arg)

    if jobDeleteOnDestination and "--delete" in args_list:
        outputPrint("Note: '--delete' removed from StandardArguments because DeleteOnDestination=true is set.")
        cleaned_args = [arg for arg in args_list if arg != "--delete"]

    if jobSourceRemote:
        if not jobSourceHostname or not jobSourceUser:
            outputPrint(f"Error: SOURCE is remote, but hostname or user is missing.")
            return "Fail"

    if jobDestinationRemote:
        if not jobDestinationHostname or not jobDestinationUser:
            outputPrint(f"Error: DESTINATION is remote, but hostname or user is missing.")
            return "Fail"

    outputPrint(f"Job validated.")
    return cleaned_args