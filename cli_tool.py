"""
for CMD:
python "cli_tool.py" --name Shai Bremer --dept DE --id 3582
Helpdesk 7080
"""

from mobileye import get_input, TasksHolder, show_message, API, LOGS_PATH, write_to_log
from mobileye import TaskExecuter, datetime, logging, os, Logger


def create_log_file(log_name: str) -> Logger:
    logger = logging.getLogger(__name__)
    path = os.path.join(LOGS_PATH, log_name)
    logging.basicConfig(filename=path, level=logging.INFO)
    return logger


def _run_tool():
    # -------- 1: User's input --------
    name, dept, task_id = get_input()

    # -------- Create log file -------
    dt_string = datetime.now().strftime("%d%m%Y_%H%M%S")
    log_name = f"task-{task_id}_dept-{dept}_time-{dt_string}.log"
    logger = create_log_file(log_name)
    write_to_log(logger, f"Task Id: {task_id}, Username: {name}, Department: {dept}")

    # -------- 2: get api data --------
    task_holder = TasksHolder(API)
    # -------- 3: check if task is exist --------
    # ask for 3 times if not exist
    is_exist, message = task_holder.check_if_exist(task_id)
    write_to_log(logger, message)
    if not is_exist:
        show_message(message)
        exit()
    # check if need to chenge id number
    if is_exist and message:
        task_id = int(message.split()[1])

    # -------- 5:check if task status is open--------
    is_open, message = task_holder.check_if_status_is_open(task_id)
    write_to_log(logger, message)
    if not is_open:
        show_message(message)
        exit()
    # -------- 6: permissions --------
    task_description = task_holder.dict[task_id].get_task_description()
    has_permission, message = task_holder.check_permission(task_description, dept)
    write_to_log(logger, message)
    if not has_permission:
        show_message("You don't have sufficient permissions")
        exit()

    # -------- DO THE TASK --------
    source = task_holder.dict[task_id].source
    destination = task_holder.dict[task_id].destination[0]
    # create destination:
    tmp_path = ""
    for dir in destination.split("/"):
        tmp_path = os.path.join(tmp_path, dir)
        if not os.path.isdir(tmp_path):
            os.makedirs(tmp_path)

    TaskExecuter.execute_task(task_description, source, destination)
    write_to_log(logger, f"{task_description} from {source[0]} to {destination} ")

if __name__ == '__main__':
    _run_tool()
