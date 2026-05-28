from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlmodel import select
from sqlmodel import Session

from jobs_hk.libs.datas import Company
from jobs_hk.libs.datas import Contact
from jobs_hk.libs.datas import Job
from jobs_hk.libs.other import get_fields_setted
from jobs_hk.libs.waiting import Waiting
from jobs_hk.types import UNSET


def _db_retry(func: callable):
    """修饰访问数据库的函数断联后尝试重连

    Args:
        func (callable): 访问数据库的函数
    Raises:
        Exception: 多次尝试重连都无法连上
    """
    
    def wrapper(*args, **kwargs):
        count_retry = 0
        while True:
            if count_retry > 10:
                raise Exception("数据库连接异常")
            try:
                result = func(*args, **kwargs)
            except OperationalError:
                count_retry += 1
                Waiting.normal(10, "[n]s 后尝试重连")
                continue
            break
        return result
    
    return wrapper


class DB:
    engine: Engine
    
    def __init__(self, engine: Engine):
        self.engine = engine
    
    @_db_retry
    def save_company(
            self,
            name: str,
            industry: str = UNSET
    ):
        payload = {
            "industry": industry
        }
        updates = get_fields_setted(payload)
    
        with Session(self.engine) as s:
            company = s.get(Company, name)
            if company:
                for field, value in updates.items():
                    setattr(company, field, value)
            else:
                s.add(Company(name=name, **updates))
            
            s.commit()
    
    @_db_retry
    def save_contact(
            self,
            alias: str,
            phone: str,
            email: str
    ):
        with Session(self.engine) as s:
            contact = s.exec(select(Contact).where(
                Contact.alias == alias,
                Contact.email == email,
                Contact.phone == phone
            )).first()
            if contact is None:
                s.add(Contact(
                    alias=alias,
                    phone=phone,
                    email=email
                ))
            
            s.commit()
            
    @_db_retry
    def save_job(
            self,
            order: str,
            name: str = UNSET,
            salary_type: str = UNSET,
            salary_min: int = UNSET,
            salary_max: int = UNSET,
            address: str = UNSET,
            company_name: str = UNSET,
            job_remark: str = UNSET,
            edu_remark: str = UNSET,
            contact_alias: str = UNSET,
            prop_remark: str = UNSET,
            compensation: str = UNSET
    ):
        payload = {
            "name": name,
            "salary_type": salary_type,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "address": address,
            "company_name": company_name,
            "job_remark": job_remark,
            "edu_remark": edu_remark,
            "contact_alias": contact_alias,
            "prop_remark": prop_remark,
            "compensation": compensation
        }
        updates = get_fields_setted(payload)

        with Session(self.engine) as s:
            job = s.get(Job, order)
            if job:
                for field, value in updates.items():
                    setattr(job, field, value)
            else:
                s.add(Job(order=order, **updates))
            
            s.commit()
    
    @_db_retry
    def get_job_without_detailed(self):
        with Session(self.engine) as s:
            job = s.exec(select(Job).where(
                Job.company == None
            )).first()
            
            return job