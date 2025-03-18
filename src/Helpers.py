import datetime
import gzip
import shutil
import subprocess
from src.ConfigHandler import *

def initialize_logging(logLvl, debugLvl, fileLogging):
    """
    Initialize logging settings.
    """
    global log_level, debug_level, file_log_enabled, session_started
    log_level = logLvl
    debug_level = debugLvl
    file_log_enabled = fileLogging
    session_started = False

def get_log_file_path():
    """
    Retrieve the log file path from the configuration.
    """
    log_dir = get_config("LOGGING", "logPath")
    #debug_print(f"Log directory resolved to: {log_dir}")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "BackUpLog.log")
    #debug_print(f"Log file path set to: {log_path}")
    return log_path

def write_to_log_file(message):
    """
    Write a message to the log file if logging is enabled.
    """
    global session_started
    if not file_log_enabled:
        debug_print("File logging is disabled. Skipping log write.")
        return

    log_file = get_log_file_path()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

    if not session_started:
        debug_print(f"Starting new log session for {timestamp}")
        with open(log_file, "a") as log:
            log.write(f"\n\n=== Log for {timestamp} ===\n\n")
        session_started = True

    with open(log_file, "a") as log:
        log.write(message + "\n")

def is_header_written(log_file, today):
    """
    Check if the log header for today has already been written.
    """
    with open(log_file, "r") as log:
        for line in log:
            if line.strip() == f"=== Log for {today} ===":
                return True
    return False

def rotate_logs():
    """
    Rotate logs every 30 days by compressing and archiving old logs.
    """
    log_file = get_log_file_path()
    log_dir = os.path.dirname(log_file)

    if os.path.exists(log_file) and days_since_creation(log_file) >= 30:
        debug_print("Log file is older than 30 days. Rotating logs.")
        backup_1 = os.path.join(log_dir, "BackUpLog-1.log")
        backup_3 = os.path.join(log_dir, "BackUpLog-3.gz")

        if os.path.exists(backup_1):
            debug_print(f"Compressing old log file: {backup_1} -> {backup_3}")
            with open(backup_1, "rb") as f_in, gzip.open(backup_3, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(backup_1)

        debug_print(f"Archiving current log file to {backup_1}")
        shutil.move(log_file, backup_1)
    else:
        debug_print("Logfile rotation not needed.")

def days_since_creation(file_path):
    """
    Calculate the number of days since a file was created.
    """
    creation_time = os.path.getctime(file_path)
    return (datetime.datetime.now() - datetime.datetime.fromtimestamp(creation_time)).days

def output_print(message):
    """
    Print and log a message based on the log level.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] -- {message}"

    if log_level >= "1":
        print(formatted_message)
    if file_log_enabled >= "1":
        write_to_log_file(formatted_message)

def debug_print(message):
    """
    Print a debug message if debug mode is enabled.
    """
    if int(debug_level) < 1:
        return
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] -- \033[1;31m{message}\033[0m")

def check_path_valid(path):
    """
    Check if a given path exists.
    """
    if not os.path.exists(path):
        return False
    return True

def exit_on_error(message):
    """
    Print an error message and exit the program.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] -- \033[1;31m{message}\033[0m")
    exit(1)

def string_to_bool(s):
    """
    Convert a string value to a boolean.
    """
    if s is not None:
        return s.strip().lower() == "true"
    else:
        return None

def get_folder_size(path, remote=False, ssh_user=None, ssh_host=None):
    """
    Retrieve the size of a folder in bytes. Supports both local and remote (SSH) paths.
    """
    try:
        if remote:
            cmd = ["ssh", f"{ssh_user}@{ssh_host}", f'du -s "{path}"']
            debug_print(f"Checking remote folder size: {ssh_user}@{ssh_host}:{path}")
        else:
            cmd = ["du", "-s", path]
            debug_print(f"Checking local folder size: {path}")

        result = subprocess.run(cmd, capture_output=True, text=True)
        size = int(result.stdout.split()[0])*1000
        debug_print(f"Folder size calculated: {size} bytes")
        return size
    except Exception as e:
        output_print(f"Error retrieving folder size: {e}")
        return 0