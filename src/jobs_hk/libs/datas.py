from typing import List
from typing import Optional

from sqlmodel import SQLModel
from sqlmodel import Relationship
from sqlmodel import Field


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    order: Optional[str] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None)
    salary: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    company_name: Optional[str] = Field(default=None, foreign_key="companies.name")
    job_remark: Optional[str] = Field(default=None)
    edu_remark: Optional[str] = Field(default=None)
    openup_remark: Optional[str] = Field(default=None)
    prop_remark: Optional[str] = Field(default=None)
    compensation: Optional[str] = Field(default=None)
    
    company: Optional["Company"] = Relationship(back_populates="jobs")


class Company(SQLModel, table=True):
    __tablename__ = "companies"

    name: Optional[str] = Field(default=None, primary_key=True)
    industry: Optional[str] = Field(default=None)
    
    jobs: List[Job] = Relationship(back_populates="company")
    