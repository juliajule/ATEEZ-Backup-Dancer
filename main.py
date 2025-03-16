#!/usr/bin/env python

from src.RsyncHandler import *
from src.CpHandler import *
from src.SftpHandler import *
from src.MailHandler import *
from src.SnapshotHandler import *

version = 0.1

configCheck()
logLevel = getConfig("DEFAULT", "logLevel") or "1"
debugLevel = getConfig("DEFAULT", "debug") or "0"
fileLogging = getConfig("DEFAULT", "fileLogging") or "0"
Level(logLevel, debugLevel, fileLogging)
debugPrint(f"Log level: {logLevel} -- Debug level: {debugLevel} -- File logging: {fileLogging}")

#####
outputPrint(f"Welcome to ATEEZ Backup Dancer {version}")
outputPrint("Startet successfully")
outputPrint("\n----")
#######

# Getting all Job Files
jobs = getJobList() or debugPrint(f"Jobs directory does not exist or has no valid .job Files") & exit(0)
outputPrint(f"Found {len(jobs)} jobs:")
for job in jobs:
    outputPrint(f"{job}")
outputPrint("\n----")

# Loop for all Jobs
jobCounter = 1
for job in jobs:
    outputPrint(f"Start Job {jobCounter} ({job})")
    jobType = getJobInfo(job, "MAIN", "type")
    jobActive = stringToBool(getJobInfo(job, "MAIN", "active"))
    outputPrint(f" Job Type:     {jobType}")
    if jobType == "snapshot" and jobActive:
        snapshotJob(job)
    if jobType == "snapshot" and not jobActive:
        outputPrint("Skipping snapshot Job")
        debugPrint(f"Snapshot job is not activated in Job-File {job}")
    if jobType == "rsync" and jobActive:
        rsyncJob(job)
    if jobType == "rsync" and not jobActive:
        outputPrint("Skipping rsync job")
        debugPrint(f"rsync job is not activated in Job-File {job}")
    if jobType == "sftp" and jobActive:
        sftpJob(job)
    if jobType == "sftp" and not jobActive:
        outputPrint("Skipping sftp job")
        debugPrint(f"sftp job is not activated in Job-File {job}")
    if jobType == "cp" and jobActive:
        cpJob(job)
    if jobType == "cp" and not jobActive:
        outputPrint("Skipping cp job")
        debugPrint(f"cp job is not activated in Job-File {job}")
    if jobType == "jobReport" and jobActive:
        generateHtml(job)
    if jobType == "jobReport" and not jobActive:
        outputPrint("Skipping cp job")
        debugPrint(f"cp job is not activated in Job-File {job}")
    if jobType == "mail" and jobActive:
        mailJob(job)
    if jobType == "mail" and not jobActive:
        outputPrint("Skipping mail job")
        debugPrint(f"mail job is not activated in Job-File {job}")
    jobCounter += 1
    outputPrint("\n----")