import functools
import threading
from datetime import datetime as DateTime
from typing import Dict
from typing import Iterable
from typing import Literal
from typing import Tuple

from jobs_hk.datas import Job


__all__ = [
    "Task",
    "Queue",
    "QueueMT"
]


def thread_lock(func):
    @functools.wraps(func)
    def wrapper(self: "QueueMT", *args, **kwargs):
        with self.lock:
            result = func(self, *args, **kwargs)
        return result
    return wrapper


class Task:
    job: Job
    status: Literal["Pendding", "Running", "Completed", "Failed"]
    date_time: DateTime

    def __init__(self, job: Job):
        self.job = job
        self.status = "Pendding"
        self.date_time = None

    def __eq__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        
        return self.job == other.job
    
    def __hash__(self):
        return hash((self.job.order, self.job.name))
    
    def __repr__(self):
        return f"Task(status={self.status}, job_name={self.job.name})"


class Queue:
    tasks: Dict[str, Task]
    
    def __init__(
            self,
            tasks: Iterable[Task]
    ):
        self.tasks = {}
        for task in tasks:
            key = str(hash(task))
            self.tasks[key] = task
        
    def get_task(self, task_key: str):
        task = self.tasks.get(task_key, None)

        if not task:
            raise Exception("Task not found")

        return task
        
    def get_tasks(
            self,
            status: Literal["Pendding", "Running", "Completed", "Failed"]
    ):
        """Only get. Not modify"""
        
        return [
            task
            for task in self.tasks.values()
            if task.status == status
        ]

    def get_pendding_task_key(self):
        """Get and modify task status to `Running`"""

        for key, task in self.tasks.items():
            if task.status == "Pendding":
                task.status = "Running"
                
                return key
        
        return None

    def set_task_status(
            self,
            status: Literal["Running", "Completed", "Failed"],
            task_key: str
    ):
        task = self.get_task(task_key)

        task.status = status
        self.tasks[task_key] = task

    def set_task_date_time(
            self,
            task_key: str
    ):
        task = self.get_task(task_key)
        
        task.date_time = DateTime.now().astimezone()
        self.tasks[task_key] = task
