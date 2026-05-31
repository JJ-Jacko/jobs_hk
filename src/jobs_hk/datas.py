from typing import List
from typing import Optional

from sqlmodel import SQLModel
from sqlmodel import Relationship
from sqlmodel import Field


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    order: Optional[str] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None)
    salary_type: Optional[str] = Field(default=None)
    salary_min: Optional[int] = Field(default=None)
    salary_max: Optional[int] = Field(default=None)
    address: Optional[str] = Field(default=None)
    company_name: Optional[str] = Field(default=None, foreign_key="companies.name")
    job_remark: Optional[str] = Field(default=None)
    edu_remark: Optional[str] = Field(default=None)
    contact_alias: Optional[str] = Field(default=None, foreign_key="contacts.alias")
    prop_remark: Optional[str] = Field(default=None)
    compensation: Optional[str] = Field(default=None)
    
    company: Optional["Company"] = Relationship(back_populates="jobs")
    contact: Optional["Contact"] = Relationship(back_populates="jobs")


class Company(SQLModel, table=True):
    __tablename__ = "companies"

    name: Optional[str] = Field(default=None, primary_key=True)
    industry: Optional[str] = Field(default=None)
    
    jobs: List[Job] = Relationship(back_populates="company")


class Contact(SQLModel, table=True):
    __tablename__ = "contacts"

    id: Optional[int] = Field(default=None, primary_key=True)
    alias: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    
    jobs: List[Job] = Relationship(back_populates="contact")
    