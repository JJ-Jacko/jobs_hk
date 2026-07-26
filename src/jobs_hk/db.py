import functools
import itertools
import threading
import time
from pathlib import Path
from typing import Any
from typing import List
from typing import Dict

import sqlalchemy
import sqlalchemy.dialects as dialects
from sqlmodel import create_engine
from sqlmodel import select
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlalchemy.schema import CreateTable

from jobs_hk.datas import Company
from jobs_hk.datas import Contact
from jobs_hk.datas import Job
from jobs_hk.exceptions import DatabaseReadOnlyError
from jobs_hk.exceptions import SQLStatementExecException
from jobs_hk.other import get_fields_setted
from jobs_hk.types import UNSET


__all__ = [
    "DB",
    "DBMT"
]


def db_retry(func):
    """
    Decorator for retrying database operations in case of disconnection.
    修饰访问数据库的函数断联后尝试重连

    Raises:
        Exception: Raised when multiple attempts to reconnect fail.
        多次尝试重连都无法连上
    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in itertools.count(0):
            if attempt > 10:
                raise Exception("Database connection failed after multiple retries")
            
            try:
                result = func(*args, **kwargs)
            except sqlalchemy.exc.OperationalError as e:
                if "attempt to write a readonly database" in str(e):
                    raise DatabaseReadOnlyError
                
                time.sleep(3)
                continue
            
            break
        
        return result

    return wrapper


def thread_lock(func):
    @functools.wraps(func)
    def wrapper(self: "DB", *args, **kwargs):
        with self.lock:
            result = func(self, *args, **kwargs)
        return result
    return wrapper


class DB:
    engine: sqlalchemy.Engine
    
    def __init__(
            self,
            database_file: Path,
            *,
            read_only: bool
    ):
        """
        Args:
            read_only:
                If you only want to query data, set it True.
                Else you want to write data, set it False.

        Raises:
            FileNotFoundError: Database file does not exist when `read_only` set True.
        """
        
        if read_only:
            if not database_file.exists():
                raise FileNotFoundError((
                    f"Database file {database_file} does not exist."
                    "Can not open in read-only mode"
                ))
            
            engine = create_engine(f"sqlite:///file:{database_file}?mode=ro&uri=true")
            self.engine = engine
        else:
            engine = create_engine(f"sqlite:///{database_file}")
            self.engine = engine
            
            if not database_file.exists():
                self.__create_database()
    
    @db_retry
    def __create_database(self):
        Job.metadata.create_all(self.engine)
        Company.metadata.create_all(self.engine)
        Contact.metadata.create_all(self.engine)
    
    def get_ddl_text(self):
        ddl_text = ""
        
        for table in SQLModel.metadata.sorted_tables:
            sql_compiled = CreateTable(table).compile(dialect=dialects.sqlite.dialect())
            ddl_text += f"{str(sql_compiled).strip()};\n\n"
        
        return ddl_text
    
    @db_retry
    def save_company(
            self,
            name: str,
            industry: str = UNSET
    ) -> int:
        """
        Save company and return company id.

        Returns:
            company_id: id of company.
        """
        
        payload = {
            "industry": industry
        }
        updates = get_fields_setted(payload)
    
        with Session(self.engine) as s:
            statement = (
                select(Company)
                .where(Company.name == name)
            )
            company = s.exec(statement).first()
            
            if company:
                for field, value in updates.items():
                    setattr(company, field, value)
                
                s.commit()
                return company.id
            
            else:
                new_company = Company(name=name, **updates)
                s.add(new_company)
            
                s.commit()
                return new_company.id
    
    @db_retry
    def save_contact(
            self,
            alias: str,
            phone: str,
            email: str
    ) -> int:
        """
        Save contact and return contact id.

        Returns:
            contact_id: id of contact.
        """
        
        with Session(self.engine) as s:
            statement = (
                select(Contact)
                .where(
                    Contact.alias == alias,
                    Contact.email == email,
                    Contact.phone == phone
                )
            )
            contact = s.exec(statement).first()
            
            if contact:
                return contact.id

            else:
                new_contact = Contact(
                    alias=alias,
                    phone=phone,
                    email=email
                )
                s.add(new_contact)
            
                s.commit()
                return new_contact.id
            
    @db_retry
    def save_job(
            self,
            order: str,
            name: str = UNSET,
            salary_type: str = UNSET,
            salary_min: int = UNSET,
            salary_max: int = UNSET,
            address: str = UNSET,
            job_remark: str = UNSET,
            edu_remark: str = UNSET,
            compensation: str = UNSET,
            company_id: int = UNSET,
            contact_id: int = UNSET
    ) -> str:
        """
        Save job and return job order.

        Returns:
            job_order: id of job.
        """
        
        payload = {
            "name": name,
            "salary_type": salary_type,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "address": address,
            "job_remark": job_remark,
            "edu_remark": edu_remark,
            "compensation": compensation,
            "company_id": company_id,
            "contact_id": contact_id
        }
        updates = get_fields_setted(payload)

        with Session(self.engine) as s:
            job = s.get(Job, order)
            
            if job:
                for field, value in updates.items():
                    setattr(job, field, value)
                
                s.commit()
                return job.order
            
            else:
                new_job = Job(order=order, **updates)
                s.add(new_job)
            
                s.commit()
                return new_job.order

    @db_retry
    def get_jobs_without_detailed(self):
        with Session(self.engine) as s:
            jobs = s.exec(select(Job).where(
                Job.company == None
            )).all()
            
            return jobs

    @db_retry
    def get_jobs_basic_info(self, num: int = 10):
        """
        Get the Hongkong jobs basic information in the project database.
        
        Args:
            num: The number of the jobs basic info of Hongkong Jobs database.
        """
        
        with Session(self.engine) as s:
            statement = (
                select(
                    Job.name,
                    Job.salary_type,
                    Job.salary_min,
                    Job.salary_max,
                    Job.address
                )
                .limit(num)
            )
            infos = s.exec(statement).all()
            
        res: List[Dict[str, Any]] = [
            info._asdict()
            for info in infos
        ]
            
        return res
    
    @db_retry
    def get_jobs_specific_info(self, statement: str):
        """
        Get the Hongkong jobs specific infomation
        using an LLM-generated SQL statement in the project database
        """
        
        with Session(self.engine) as s:
            conn = s.connection()
            text_clause = sqlalchemy.text(statement)
            try:
                conn.execute(sqlalchemy.text(f"EXPLAIN {statement}"))
            except sqlalchemy.OperationalError as e:
                raise SQLStatementExecException(statement, str(e.orig))
            
            res = conn.execute(text_clause)
            
            if not res.returns_rows:
                raise SQLStatementExecException(statement, "statement did not return rows")
            
            rows = res.mappings().all()
            return rows


class DBMT(DB):
    """Database Multi Thread Support"""

    lock: threading.Lock
    
    def __init__(
            self,
            database_file: Path,
            lock: threading.Lock,
            *,
            read_only: bool
    ):
        """
        Args:
            read_only:
                If you only want to query data, set it True.
                Else you want to write data, set it False.

        Raises:
            FileNotFoundError: Database file does not exist when `read_only` set True.
        """
        
        super().__init__(database_file, read_only=read_only)
        self.lock = lock
    
    @thread_lock
    def save_company(self, name, industry = UNSET):
        return super().save_company(name, industry)
    
    @thread_lock
    def save_contact(self, alias, phone, email):
        return super().save_contact(alias, phone, email)
    
    @thread_lock
    def save_job(
            self,
            order, name = UNSET, salary_type = UNSET,
            salary_min = UNSET, salary_max = UNSET, address = UNSET,
            company_name = UNSET, job_remark = UNSET, edu_remark = UNSET,
            contact_alias = UNSET, compensation = UNSET
    ):
        return super().save_job(
            order, name, salary_type,
            salary_min, salary_max, address,
            company_name, job_remark, edu_remark,
            contact_alias, compensation
        )
    
    @thread_lock
    def get_jobs_without_detailed(self):
        return super().get_jobs_without_detailed()
    
    @thread_lock
    def get_jobs_basic_info(self, limit = 10):
        return super().get_jobs_basic_info(limit)
    
    @thread_lock
    def get_jobs_specific_info(self, statement):
        return super().get_jobs_specific_info(statement)