from jobs_hk.libs.db import DB
from jobs_hk.libs.env import get_engine
from jobs_hk.libs.env import init_database
from jobs_hk.libs.filter import JobCardFilter
from jobs_hk.libs.filter import JobSearchFilter
from jobs_hk.libs.log import get_logger
from jobs_hk.libs.waiting import Waiting
from jobs_hk.libs.web import Web


engine = get_engine()
init_database(engine)
db = DB(engine)

def search():
    logger = get_logger("search")
    Waiting.set_up(10, 20, 5, 15)
    
    page = 1
    while True:
        logger.info(f"Processing page: {page}")
        
        resp = Web.job_search(page)
        sf = JobSearchFilter(resp.text)
        total_pages = sf.get_total_pages()
        jobs = sf.get_jobs()
        
        for job in jobs:
            db.save_job(
                order=job["order"],
                name=job["name"],
                salary_type=job["salary_type"],
                salary_min=job["salary_min"],
                salary_max=job["salary_max"],
                address=job["address"]
            )
        
        if page > total_pages:
            break
        page += 1
        Waiting.random()


def fill():
    logger = get_logger("fill")
    Waiting.set_up(10, 20, 3, 8)
    
    while (job := db.get_job_without_detailed()):
        logger.info(f"Processing job: {job.name}")
        
        resp = Web.job_card(job.order)
        cf = JobCardFilter(resp.text)
        job_info = cf.get_job_info()

        db.save_company(
            name=job_info["company_name"],
            industry=job_info["industry"]
        )
        db.save_contact(
            alias=job_info["alias"],
            phone=job_info["phone"],
            email=job_info["email"]
        )
        db.save_job(
            order=job.order,
            company_name=job_info["company_name"],
            job_remark=job_info["job_remark"],
            edu_remark=job_info["edu_remark"],
            contact_alias=job_info["alias"],
            prop_remark=job_info["prop_remark"],
            compensation=job_info["compensation"]
        )
        
        Waiting.random()


if __name__ == "__main__":
    # search()
    # fill()
    pass