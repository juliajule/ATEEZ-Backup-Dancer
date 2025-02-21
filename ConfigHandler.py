import os
import configparser

def configCheck():
    config_file = "Config.ini"
    if os.path.isfile(config_file):
        return True
    else:
        return False

def getConfig(section, key):
    config_file = "Config.ini"
    config = configparser.ConfigParser()
    config.read(config_file)

    if section in config:
        return config[section].get(key, None)
    else:
        return None

