import datetime
import os

def Level(logLvl, debugLvl):
    global logLevel
    logLevel = logLvl
    global debugLevel
    debugLevel = debugLvl

def outputPrint(message):
    if logLevel < "1":
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] -- \033[1;37m{message}\033[0m")

def debugPrint(message):
    if int(debugLevel) < 1:
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] -- \033[1;31m{message}\033[0m")

def check_path_valid(path):
    if not os.path.exists(path):
        return False
    return True

def exitOnError(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] -- \033[1;31m{message}\033[0m")
    exit(1)
