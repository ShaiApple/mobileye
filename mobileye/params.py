from mobileye import os, Logger

API = "https://dct-tasks-db.herokuapp.com/tasks"
PERMISSIONS_FILE = open(os.path.join('source', 'auth', 'permissions.json'))
LOGS_PATH = os.path.join('destination', 'logs')


def print_to_console(message: str):
    print(message)


def write_to_log(logger: Logger, message: str):
    if message:
        logger.info(message)
