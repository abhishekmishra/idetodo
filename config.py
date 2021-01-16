import configparser

_CONFIG_FILE = "idetodo.ini"


def read_config():
    config = configparser.ConfigParser()
    config.read(_CONFIG_FILE)
    return config
