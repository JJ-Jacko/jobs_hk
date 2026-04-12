from sqlalchemy.engine import Engine
from sqlmodel import create_engine

from jobs_hk.libs.datas import Job
from jobs_hk.libs.datas import Company
from jobs_hk.libs.datas import Contact


def get_engine(file: str = "data.db"):
    
    return create_engine(f"sqlite:///{file}")


def init_database(engine: Engine):
    Job.metadata.create_all(engine)
    Company.metadata.create_all(engine)
    Contact.metadata.create_all(engine)
