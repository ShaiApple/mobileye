from mobileye import urlopen, json, typing, shutil, glob, os, PERMISSIONS_FILE


class TasksHolder:
    def __init__(self, url):
        self.dict = self.prepare_dict(url)
        # Get permissions data
        data = json.load(PERMISSIONS_FILE)
        self.permissions_data = dict((k.lower(), v) for k, v in data.items())

    def prepare_dict(self, url) -> dict:
        """
        :param url: Given url to get data
        :return: dict {int : task object}
        """
        response = urlopen(url)
        jsonString = json.loads(response.read())
        all_tasks = dict()
        for task_dict in jsonString:
            task = Task(task_dict)
            all_tasks[task_dict["id"]] = task
        return all_tasks

    def check_if_exist(self, id: int, attempt=1) -> typing.Tuple[bool, str]:
        """
        :param id: task id
        :param attempt: give the user 3 attempts to get valid id
        :return: bool: true if exist, else false
                 message info
        """

        if id in self.dict.keys():
            msg = ""
            return True, msg
        else:
            while (attempt < 3):
                attempt += 1
                id = int(input(f"{id} does not exist. please enter ID again ({attempt}/3): "))
                if id in self.dict.keys():
                    return True, f"Id {id} exist on {attempt} attemot"
            if attempt == 3:
                msg = "Id exist check failed 3 time. exit."
                return False, msg

    def check_if_status_is_open(self, id: int) -> typing.Tuple[bool, str]:
        """
        :param id: task id
        :return: bool if open- true, message info
        """
        if self.dict[id].get_status() == "open":
            msg = "task status is open."
            return True, msg
        else:
            msg = f"The task cannot be executed due to its status ({self.dict[id].get_status()}). exit."
            return False, msg

    def check_permission(self, task_description: str, dept: str) -> bool:
        true_msg = f"{dept} have permission"
        false_msg = f"{dept} have no permission. exit."
        permissions = self.permissions_data[dept.lower()]
        if permissions is None:
            return False, false_msg
        elif isinstance(permissions, list):
            for permission in permissions:
                if self.inner_check_permission(task_description, permission):
                    return True, true_msg
            # permission not in list, so there is no permission.
            return False, false_msg

        elif isinstance(permissions, str):
            if self.inner_check_permission(task_description, permissions):
                return True, true_msg
            else:
                return False, false_msg

    def inner_check_permission(self, task_description, permission) -> bool:

        if task_description.lower().startswith(permission.lower()):
            # Copy latest, Copy haviest
            return True
        elif permission.lower() == 'Copy named with'.lower():
            # copy file with
            return True
        else:
            return False


class Task:
    def __init__(self, task_info):
        self.id = task_info["id"],
        self.created_time = task_info["created_at"],
        self.description = task_info["description"],
        self.source = task_info["source"],
        self.destination = task_info["destination"],
        self.status = task_info["status"]

    def get_task_description(self):
        return self.description[0]

    def get_status(self):
        return self.status


class TaskExecuter:
    @staticmethod
    def execute_task(task_description, source, destination):
        if task_description.startswith("Copy latest"):
            TaskExecuter.copy_latest(source, destination, task_description)
        elif task_description.startswith("Copy heaviest"):
            TaskExecuter.copy_heaviest(source, destination, task_description)
        elif task_description.startswith("Copy") and "file named with" in task_description:
            TaskExecuter.copy_with(source, destination, task_description)
        else:
            raise Exception("Unknown case!!")

    @staticmethod
    def copy_with(source, destination, description):
        extension = description.split(" ")[2]
        sub_file_name = description.lower().split("file named with ")[1]
        file_path = os.path.join(source[0], f"*{sub_file_name}*.{extension}")
        files = glob.glob(file_path)
        if len(files) == 1:
            shutil.copy(files[0], destination)
        else:
            raise Exception("Too many files in copy_with")

    @staticmethod
    def copy_heaviest(source, destination, description):
        extension = description.lower().split("copy heaviest ")[1].split(" ")[0]
        file_path = os.path.join(source[0], f"*.{extension}")
        files = glob.glob(file_path)
        if len(files) > 0:
            heaviest_file = files[0]
            heaviest_file_size = os.path.getsize(heaviest_file)
            for cur_file in files[1:]:
                # we assume there are no 2 files with the same size (in that case we will copy the first one)
                cur_size = os.path.getsize(cur_file)
                if cur_size > heaviest_file_size:
                    heaviest_file = cur_file
                    heaviest_file_size = cur_size

            shutil.copy(heaviest_file, destination)
        else:
            raise Exception("couldn't find any files in copy_heaviest")

    @staticmethod
    def copy_latest(source, destination, description):
        extension = description.split(" ")[2]
        file_path = os.path.join(source[0], f"*.{extension}")
        files = glob.glob(file_path)
        if len(files) > 0:
            latest_file = files[0]
            latest_file_modification_date = os.path.getmtime(latest_file)
            for cur_file in files[1:]:  # we assume there are no 2 files with the same modification date
                cur_date = os.path.getmtime(cur_file)
                if cur_date > latest_file_modification_date:
                    latest_file = cur_file
                    latest_file_modification_date = cur_date

            shutil.copy(latest_file, destination)
        else:
            raise Exception("couldn't find any files in copy_latest")
