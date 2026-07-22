import functools
import threading
from abc import ABC
from abc import abstractmethod
from datetime import datetime as DateTime
from typing import Dict
from typing import List
from typing import Literal

from jobs_hk.datas import Job


__all__ = [
    "Task",
    "TaskS",
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


class TaskBase(ABC):
    status: Literal["Pendding", "Running", "Completed", "Failed"]
    date_time: DateTime

    def __init__(self):
        self.status = "Pendding"
        self.date_time = None

    def __eq__(self, other):
        return self._eq_impl(other)
    
    def __hash__(self):
        return self._hash_impl()
    
    def __repr__(self):
        infos_str = f"status={self.status}"
        
        for info, value in self._repr_extra_infos().items():
            info_str = f"{info}={value}"
            infos_str += f", {info_str}"
        
        return f"{type(self).__name__}({infos_str})"
    
    @abstractmethod
    def _eq_impl(self, other) -> bool:
        ...
        
    @abstractmethod
    def _hash_impl(self) -> int:
        ...
    
    @abstractmethod
    def _repr_extra_infos(self) -> Dict[str, str]:
        ...


class Task(TaskBase):
    job: Job

    def __init__(self, job: Job):
        super().__init__()
        self.job = job

    def _eq_impl(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        
        return self.job == other.job

    def _hash_impl(self):
        return hash((self.job.order, self.job.name))
    
    def _repr_extra_infos(self):
        return {
            "job_name": self.job.name
        }
    

class TaskS(TaskBase):
    page: int

    def __init__(self, page: int):
        super().__init__()
        self.page = page
    
    def _eq_impl(self, other):
        if not isinstance(other, TaskS):
            return NotImplemented
        
        return self.page == other.page
    
    def _hash_impl(self):
        return hash((self.page, "salt"))
    
    def _repr_extra_infos(self):
        return {
            "page": str(self.page)
        }
    

class Queue:
    tasks: Dict[str, TaskBase]
    
    def __init__(
            self,
            tasks: List[TaskBase]
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
            status: Literal["Pendding", "Running", "Completed", "Failed"],
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


class QueueMT(Queue):
    """Queue Multi Thread Support"""
    
    lock: threading.Lock
    
    def __init__(
            self,
            tasks: List[TaskBase],
            lock: threading.Lock
    ):
        super().__init__(tasks)
        self.lock = lock
    
    @thread_lock
    def get_pendding_task_key(self):
        return super().get_pendding_task_key()
    
    @thread_lock
    def set_task_status(self, status, task_key):
        return super().set_task_status(status, task_key)
    
    @thread_lock
    def set_task_date_time(self, task_key):
        return super().set_task_date_time(task_key)