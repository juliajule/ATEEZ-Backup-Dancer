import os
import configparser

def getJobList():
    job_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../jobs"))

    if not os.path.isdir(job_dir):
        return False

    job_files = [f for f in os.listdir(job_dir) if f.endswith(".job")]
    job_files.sort(key=lambda x: int(x.split('-')[0]))

    return job_files

def getJobInfo(file, section, key):
    job_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../jobs", file))
    config = configparser.ConfigParser()
    config.read(job_file)

    if section in config:
        value = config[section].get(key, None)
        if value is not None:
            return value.strip('"').strip("'")
    else:
        return None