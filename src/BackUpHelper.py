import os
import configparser
from src.Helpers import debug_print


def get_job_list():
    """
    Retrieves a list of available job configuration files.

    Returns:
        list: A sorted list of job file names or an empty list if no jobs exist.
    """
    job_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../jobs"))

    if not os.path.isdir(job_dir):
        debug_print(f"Job directory does not exist: {job_dir}")
        return False

    job_files = [f for f in os.listdir(job_dir) if f.endswith(".job")]
    job_files.sort(key=lambda x: int(x.split('-')[0]))

    debug_print(f"Found {len(job_files)} job files: {job_files}")
    return job_files

def get_job_info(file, section, key):
    """
    Retrieves a specific key's value from a given job configuration file.

    Args:
        file (str): The job file name.
        section (str): The section in the configuration file.
        key (str): The key whose value needs to be retrieved.

    Returns:
        str or None: The value of the key, stripped of quotes, or None if not found.
    """
    job_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../jobs", file))

    if not os.path.isfile(job_file):
        debug_print(f"Job file does not exist: {job_file}")
        return None

    config = configparser.ConfigParser()
    config.read(job_file)

    if section in config and key in config[section]:
        value = config[section].get(key, None)
        if value is not None:
            stripped_value = value.strip('"').strip("'")
            if key == "password":
                debug_print(f"Found password from {file} [{section}] {key}")
            else:
                debug_print(f"Retrieved value from {file} [{section}] {key}: {stripped_value}")
            return stripped_value
    else:
        debug_print(f"Key '{key}' not found in section '{section}' of {file}")
        return None