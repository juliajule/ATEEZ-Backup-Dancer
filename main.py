#!/usr/bin/env python

from ConfigHandler import *
from Helpers import *

version = 1.0
configCheck()
logLevel = getConfig("DEFAULT", "logLevel") or "1"
debugLevel = getConfig("DEFAULT", "debug") or "0"
Level(logLevel, debugLevel)
debugPrint(f"Log level: {logLevel}")

#####
outputPrint(f"Welcome to ATEEZ Backup Dancer {version}")
outputPrint("Startet successfully")
outputPrint("----")
