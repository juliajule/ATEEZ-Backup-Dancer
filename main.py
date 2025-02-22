#!/usr/bin/env python

from ConfigHandler import *
from Helpers import *

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

# Checkt, ob die Requirements aus der Config vorhanden sind
# Check 1: rsync
rsync = getConfig("REQUIREMENT", "rsync")
debugPrint(f"rsync: {rsync}")
check_path_valid(rsync) or exitOnError("rsync Path in Config does not exist")


