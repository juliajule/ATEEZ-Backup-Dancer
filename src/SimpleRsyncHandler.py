from src.BackUpHelper import *
from src.Helpers import *

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
    jobDestionationPath = getJobInfo(job, "DESTINATION", "Path")

    #Logic Checks
    if jobSourceRemote and jobDestinationRemote:
        debugPrint(f"{jobSourceRemote} -> {jobDestinationRemote}")
        outputPrint("Error: Source and destination are both remote, Job ends")
        return

    rsyncLine = "rsync"

    if jobStandardArguments != None:
        rsyncLine = rsyncLine + " -" + jobStandardArguments

    if jobDeleteOnDestination:
        rsyncLine = rsyncLine + " --delete "

    if jobSourceHostname and jobSourceRemote:
        rsyncLine = rsyncLine + jobSourceUser + "@" + jobSourceHostname + ":" + jobSourcePath + " " + jobDestionationPath

    if jobDestinationHostname and jobDestinationRemote:
        rsyncLine = rsyncLine + jobSourcePath + " " + jobDestinationUser + "@" + jobDestinationHostname + ":" + jobDestionationPath

    if not (jobSourceRemote or jobDestinationRemote):
        rsyncLine = rsyncLine + jobSourcePath + " " + jobDestionationPath


    outputPrint(rsyncLine)