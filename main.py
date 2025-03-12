#!/usr/bin/env python

from src.SimpleRsyncHandler import *
from src.CpHandler import *
from src.SftpHandler import *

version = 0.1

configCheck()
logLevel = getConfig("DEFAULT", "logLevel") or "1"
debugLevel = getConfig("DEFAULT", "debug") or "0"
Level(logLevel, debugLevel)
debugPrint(f"Log level: {logLevel} -- Debug level: {debugLevel}")

#####
outputPrint(f"Welcome to ATEEZ Backup Dancer {version}")
outputPrint("Startet successfully")
outputPrint("----")
#######

# Getting all Job Files
jobs = getJobList() or debugPrint(f"Jobs directory does not exist or has no valid .job Files") & exit(0)
outputPrint(f"Found {len(jobs)} jobs:")
for job in jobs:
    outputPrint(f"{job}")

# Loop for all Jobs
jobCounter = 1
for job in jobs:
    outputPrint(f"Start Job {jobCounter} ({job})")
    jobType = getJobInfo(job, "MAIN", "type")
    outputPrint(f" Job Type:     {jobType}")
    if jobType == "rsync":
        rsyncJob(job)
    if jobType == "sftp":
        sftpJob(job)
    if jobType == "cp":
        cpJob(job)
    jobCounter += 1


