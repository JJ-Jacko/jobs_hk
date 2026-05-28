import jobs_hk.cli.context as context
from jobs_hk.filters.job_card_filter import JobCardFilter
from jobs_hk.libs.log import get_logger
from jobs_hk.libs.waiting import Waiting
from jobs_hk.libs.web import Web


def run():
    logger = get_logger("fill")
    Waiting.set_up(10, 20, 3, 8)
    
    while (job := context.db.get_job_without_detailed()):
        logger.info(f"Processing job: {job.name}")
        
        resp = Web.job_card(job.order)
        cf = JobCardFilter(resp.text)
        job_info = cf.get_job_info()

        context.db.save_company(
            name=job_info["company_name"],
            industry=job_info["industry"]
        )
        context.db.save_contact(
            alias=job_info["alias"],
            phone=job_info["phone"],
            email=job_info["email"]
        )
        context.db.save_job(
            order=job.order,
            company_name=job_info["company_name"],
            job_remark=job_info["job_remark"],
            edu_remark=job_info["edu_remark"],
            contact_alias=job_info["alias"],
            prop_remark=job_info["prop_remark"],
            compensation=job_info["compensation"]
        )
        
        Waiting.random()
