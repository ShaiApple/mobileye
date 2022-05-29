from mobileye import os, Logger

API = "https://dct-tasks-db.herokuapp.com/tasks"
PERMISSIONS_FILE = open(os.path.join('source', 'auth', 'permissions.json'))
LOGS_PATH = os.path.join('destination', 'logs')
# check if exist:
if not os.path.isdir(LOGS_PATH):
    os.makedirs(LOGS_PATH)


def print_to_console(message: str):
    print(message)


def write_to_log(logger: Logger, message: str):
    if message:
        logger.info(message)