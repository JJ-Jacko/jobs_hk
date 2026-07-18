import threading
import time
from logging import Logger

import jobs_hk.context as context
from jobs_hk.filters.job_card_filter import JobCardFilter
from jobs_hk.log import get_logger
from jobs_hk.queue_manager import QueueMT
from jobs_hk.queue_manager import Task
from jobs_hk.waiting import Waiting
from jobs_hk.web import JobGovHK


def worker(
        logger: Logger,
        offset: int,
        queue: QueueMT
):
    waiting = Waiting()
    web = JobGovHK(
        context.project_config["proxy"]["host"],
        context.project_config["proxy"]["port_start"] + offset
    )
    
    while (task_key := queue.get_pendding_task_key()):
        job = queue.get_task(task_key).job
        logger.info(f"Processing job: {job.name}")
        
        resp = web.job_card(job.order)
        filter = JobCardFilter(resp.text)
        job_info = filter.get_job_info()

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
        
        queue.set_task_status("Completed", task_key)
        queue.set_task_date_time(task_key)
        waiting.random(show_info=False)


def run():
    logger = get_logger("fill_multi_threads")
    lock = threading.Lock()
    queue = QueueMT(
        [
            Task(job)
            for job in context.db.get_jobs_without_detailed()
        ],
        lock
    )
    
    threads = [
        threading.Thread(
            target=worker,
            kwargs={
                "logger": logger,
                "offset": i,
                "queue": queue
            },
            name=f"Worker-{i + 1}"
        )
        for i in range(context.project_config["proxy"]["offset"])
    ]
    for t in threads:
        t.start()
        time.sleep(3)
    for t in threads:
        t.join()
        