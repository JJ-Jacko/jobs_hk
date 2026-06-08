import itertools

import jobs_hk.cli.context as context
from jobs_hk.filters.job_search_filter import JobSearchFilter
from jobs_hk.log import get_logger
from jobs_hk.waiting import Waiting
from jobs_hk.web import JobGovHK


def run():
    logger = get_logger("search")
    Waiting.set_up(10, 20, 5, 15)
    web = JobGovHK()
    
    for page in itertools.count(1):
        logger.info(f"Processing page: {page}")
        
        resp = web.job_search(page)
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
        
        Waiting.random()
