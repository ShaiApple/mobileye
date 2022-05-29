from mobileye import os, Logger


API = "https://dct-tasks-db.herokuapp.com/tasks"
PERMISSIONS_FILE = open("source\\auth\permissions.json")
LOGS_PATH = "destination\logs"


def check_folder(base_path, file_name):
    if not os.path.exists(os.path.join(base_path)):
        os.makedirs(file_name)

def print_to_console(message: str):
    print(message)

def write_to_log(logger: Logger, message: str):
    if message:
        print_to_console(message)
        logger.info(message)
