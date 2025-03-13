import datetime
import gzip
import shutil
from src.ConfigHandler import *

def Level(logLvl, debugLvl, fileLogging):
    global logLevel
    global debugLevel
    global fileLoggingEnabled
    global sessionStarted
    logLevel = logLvl
    debugLevel = debugLvl
    fileLoggingEnabled = fileLogging
    sessionStarted = False

def getLogFilePath():
    log_dir = getConfig("DEFAULT", "logPath")
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, "BackUpLog.log")

def writeToLogFile(message):
    global sessionStarted
    if not fileLoggingEnabled:
        return

    log_file = getLogFilePath()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

    if not sessionStarted:
        with open(log_file, "a") as log:
            log.write(f"\n\n=== Log für {timestamp} ===\n\n")
        sessionStarted = True

    with open(log_file, "a") as log:
        log.write(message + "\n")

    rotateLogs()

def isHeaderWritten(log_file, today):
    with open(log_file, "r") as log:
        for line in log:
            if line.strip() == f"=== Log für {today} ===":
                return True
    return False

def rotateLogs():
    log_file = getLogFilePath()
    log_dir = os.path.dirname(log_file)

    if os.path.exists(log_file) and daysSinceCreation(log_file) >= 30:
        backup_1 = os.path.join(log_dir, "BackUpLog-1.log")
        backup_3 = os.path.join(log_dir, "BackUpLog-3.gz")

        if os.path.exists(backup_1):
            with open(backup_1, "rb") as f_in, gzip.open(backup_3, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(backup_1)

        shutil.move(log_file, backup_1)

def daysSinceCreation(file_path):
    creation_time = os.path.getctime(file_path)
    return (datetime.datetime.now() - datetime.datetime.fromtimestamp(creation_time)).days

def outputPrint(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #formatted_message = f"[{timestamp}] -- \033[1;37m{message}\033[0m"
    formatted_message = f"[{timestamp}] -- {message}"

    if logLevel >= "1":
        print(formatted_message)

    writeToLogFile(formatted_message)

def debugPrint(message):
    if int(debugLevel) < 1:
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] -- \033[1;31m{message}\033[0m")

def checkPathValid(path):
    if not os.path.exists(path):
        return False
    return True

def exitOnError(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] -- \033[1;31m{message}\033[0m")
    exit(1)

def stringToBool(s):
    return s.strip().lower() == "true"
