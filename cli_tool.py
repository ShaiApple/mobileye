"""
for CMD:
python "cli_tool.py" --name Shai Bremer --dept DE --id 3582
Helpdesk 7080
"""

from mobileye import  TasksHolder, print_to_console, API, LOGS_PATH, write_to_log
from mobileye import TaskExecuter, datetime, logging, os, Logger, argparse


def create_log_file(log_name: str) -> Logger:
    logger = logging.getLogger(__name__)
    path = os.path.join(LOGS_PATH, log_name)
    logging.basicConfig(filename=path, level=logging.INFO)
    return logger


def get_input() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    # --name NAME --dept DEPARTMENT --id TASK ID
    parser.add_argument("--name", nargs='*')
    parser.add_argument("--dept")
    parser.add_argument("--id", type=int)
    args = parser.parse_args()

    # handle missing args
    while (not args.name):
        args.name = input('Please enter your name: ')
    while (not args.dept):
        args.dept = input('Please enter department: ')
    while (not args.id):
        args.id = input('Please enter task id: ')

    return args.name, args.dept, int(args.id)


def _run_tool():
    # -------- 1: User's input --------
    name, dept, task_id = get_input()

    # -------- Create log file -------
    dt_string = datetime.now().strftime("%d%m%Y_%H%M%S")
    log_name = f"task-{task_id}_dept-{dept}_time-{dt_string}.log"
    logger = create_log_file(log_name)
    write_to_log(logger, f"Task Id: {task_id}, Username: {name}, Department: {dept}")

    # -------- 2: get data from api  --------
    task_holder = TasksHolder(API)
    # -------- 3: check if task is exist --------
    # ask for 3 times if not exist
    is_exist, message = task_holder.check_if_exist(task_id)
    write_to_log(logger, message)
    if not is_exist:
        print_to_console(message)
        exit()
    else:
        print_to_console(message)
    # check if need to chenge id number
    if is_exist and message:
        task_id = int(message.split()[1])

    # -------- 5:check if task status is open--------
    is_open, message = task_holder.check_if_status_is_open(task_id)
    write_to_log(logger, message)
    if not is_open:
        print_to_console(message)
        exit()
    else:
        print_to_console(message)

    # -------- 6: permissions --------
    task_description = task_holder.dict[task_id].get_task_description()
    has_permission, message = task_holder.check_permission(task_description, dept)
    write_to_log(logger, message)
    if not has_permission:
        print_to_console(message)
        exit()
    else:
        print_to_console(message)

    # -------- DO THE TASK --------
    source = task_holder.dict[task_id].get_source()
    destination = task_holder.dict[task_id].get_destination()
    # create destination:
    tmp_path = ""
    for dir in destination.split("/"):
        tmp_path = os.path.join(tmp_path, dir)
        if not os.path.isdir(tmp_path):
            os.makedirs(tmp_path)
            write_to_log(logger, f"created {tmp_path}")

    TaskExecuter.execute_task(task_description, source, destination)
    write_to_log(logger, f"{task_description} from {source} to {destination} ")


if __name__ == '__main__':
    _run_tool()
