from mobileye import urlopen, json, typing, shutil, glob, os, PERMISSIONS_FILE


class TasksHolder:
    def __init__(self, url: str):
        self.dict = self.prepare_dict(url)
        # Get permissions data
        data = json.load(PERMISSIONS_FILE)
        self.permissions_data = dict((k.lower(), v) for k, v in data.items())

    def prepare_dict(self, url) -> dict:
        """
        :param url: Given url to get data
        :return: dict {int : Task object}
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
            msg = ""  # empty because I don't to print while true
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

    def check_permission(self, task_description: str, dept: str) -> typing.Tuple[bool, str]:
        """
        check if permissions is null,str or list and sent to def inner_check_permission as str.
        :param task_description: task_description
        :param dept: dept
        :return: bool + message
        """
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

    def inner_check_permission(self, task_description: str, permission: str) -> bool:
        # Note that permission and description will always begin with capital c
        if task_description.startswith(permission) or permission == 'Copy named with':
            return True
        else:
            return False


class Task:
    def __init__(self, task_info: dict):
        self.id = task_info["id"],
        self.created_time = task_info["created_at"],
        self.description = task_info["description"],
        self.source = task_info["source"],
        self.destination = task_info["destination"],
        self.status = task_info["status"]

    # I added [0] to extract a string from tuple.
    def get_id(self) -> int:
        return self.id[0]

    def get_task_description(self) -> str:
        return self.description[0]

    def get_status(self) -> str:
        return self.status

    def get_source(self) -> str:
        return self.source[0]

    def get_destination(self) -> str:
        return self.destination[0]


class TaskExecuter:
    @staticmethod
    def execute_task(task_description: str, source: str, destination: str):
        """
        Function will check what is the task and execute the correct inner function.
        """
        if task_description.startswith("Copy latest"):
            TaskExecuter.copy_latest(source, destination, task_description)
        elif task_description.startswith("Copy heaviest"):
            TaskExecuter.copy_heaviest(source, destination, task_description)
        else:  # task_description.startswith("Copy") and "file named with" in task_description:
            TaskExecuter.copy_with(source, destination, task_description)

    @staticmethod
    def copy_with(source: str, destination: str, description: str):
        extension = description.split(" ")[2]
        sub_file_name = description.split("file named with ")[1]
        file_path = os.path.join(source, f"*{sub_file_name}*.{extension}")
        files = glob.glob(file_path)
        if len(files) == 1:
            shutil.copy(files[0], destination)
        else:
            raise Exception("Too many files in copy_with")

    @staticmethod
    def copy_heaviest(source: str, destination: str, description: str):
        """
        Loop over files and copy the heaviest one
        :param source: dir
        :param destination:dir
        :param description: the task
        """
        extension = description.split(" ")[2]
        file_path = os.path.join(source, f"*.{extension}")
        files = glob.glob(file_path)
        if len(files) > 0:
            heaviest_file = files[0]
            heaviest_file_size = os.path.getsize(heaviest_file)
            for cur_file in files[1:]:
                # I assumed there are no two similar files (in size).
                # in case two identical files are found, Iד will copy the first one.
                cur_size = os.path.getsize(cur_file)
                if cur_size > heaviest_file_size:
                    heaviest_file = cur_file
                    heaviest_file_size = cur_size

            shutil.copy(heaviest_file, destination)
        else:
            raise Exception("couldn't find any files in copy_heaviest")

    @staticmethod
    def copy_latest(source: str, destination: str, description: str):
        # Loop over files and copy the latest one
        extension = description.split(" ")[2]
        file_path = os.path.join(source, f"*.{extension}")
        files = glob.glob(file_path)
        if len(files) > 0:
            latest_file = files[0]
            latest_file_modification_date = os.path.getmtime(latest_file)
            for cur_file in files[1:]:  # I assumed there are no two files with the same modification date
                cur_date = os.path.getmtime(cur_file)
                if cur_date > latest_file_modification_date:
                    latest_file = cur_file
                    latest_file_modification_date = cur_date

            shutil.copy(latest_file, destination)
        else:
            raise Exception("couldn't find any files in copy_latest")
