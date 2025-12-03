from dataclasses import dataclass


@dataclass
class Job:
    no: str
    order: str
    name: str
    salary: str
    address: str
