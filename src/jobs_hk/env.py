import sqlalchemy.dialects as dialects
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateTable
from sqlmodel import create_engine
from sqlmodel import SQLModel

from jobs_hk.datas import Job
from jobs_hk.datas import Company
from jobs_hk.datas import Contact


def get_engine(file: str = "data.db"):
    
    return create_engine(f"sqlite:///{file}")


def init_database(engine: Engine):
    Job.metadata.create_all(engine)
    Company.metadata.create_all(engine)
    Contact.metadata.create_all(engine)


def get_ddl_text():
    ddl_text = ""
    
    for table in SQLModel.metadata.sorted_tables:
        sql_compiled = CreateTable(table).compile(dialect=dialects.sqlite.dialect())
        ddl_text += f"{str(sql_compiled).strip()};\n\n"
    
    return ddl_text