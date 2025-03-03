from src.BackUpHelper import *
from src.Helpers import *
import subprocess
import shlex

FORBIDDEN_ARGUMENTS = ["--remove-source-files", "--recursive"]

def rsyncJob(job):
    #Alle Informationen aus der Konfig
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

    rsyncLine = ["rsync"]

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

    for line in process.stdout:
        outputPrint(line.strip())

    process.stdout.close()
    returncode = process.wait()

    if returncode == 0:
        outputPrint("Rsync succeeded.")
    else:
        outputPrint(f"Error with Code {returncode}.")


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
            return

    if jobDestinationRemote:
        if not jobDestinationHostname or not jobDestinationUser:
            outputPrint(f"Error: DESTINATION is remote, but hostname or user is missing.")
            return

    outputPrint(f"Job validated.")
    return cleaned_args