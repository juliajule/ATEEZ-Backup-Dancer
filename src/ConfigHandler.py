import os
import configparser

def configCheck():
    global config_file
    config_file = os.path.join(os.path.dirname(__file__), "../Config.ini")
    if os.path.isfile(config_file):
        return True
    else:
        return False

def getConfig(section, key):
    config = configparser.ConfigParser()
    config.read(config_file)

    if section in config:
        return config[section].get(key, None).strip('"').strip("'")
    else:
        return None

