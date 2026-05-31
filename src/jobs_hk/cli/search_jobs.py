import jobs_hk.cli.context as context
from jobs_hk.filters.job_search_filter import JobSearchFilter
from jobs_hk.log import get_logger
from jobs_hk.waiting import Waiting
from jobs_hk.web import Web


def run():
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
            context.db.save_job(
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
