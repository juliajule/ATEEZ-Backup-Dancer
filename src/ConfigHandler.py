import os
import configparser

def config_check():
    """
    Checks if the configuration file exists.
    Returns:
        bool: True if the file exists, False otherwise.
    """
    global config_file
    config_file = os.path.join(os.path.dirname(__file__), "../Config.ini")

    if os.path.isfile(config_file):
        return True
    else:
        print(f"Config file not found: {config_file}")
        return False

def get_config(section, key):
    """
    Retrieves a configuration value from the config file.
    Args:
        section (str): The section name in the config file.
        key (str): The key whose value needs to be retrieved.
    Returns:
        str or None: The value if found, otherwise None.
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    if section in config and key in config[section]:
        return config[section].get(key, None).strip('"').strip("'")
    else:
        print(f"Config key or section not found: [{section}] {key}, using default for {key}")
        return None

