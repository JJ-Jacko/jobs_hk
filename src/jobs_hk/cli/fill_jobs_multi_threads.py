import threading
import time
from logging import Logger

import jobs_hk.context as context
from jobs_hk.exceptions import NeedWaiting
from jobs_hk.exceptions import WebRetryExansted
from jobs_hk.filters.job_card_filter import JobCardFilter
from jobs_hk.log import get_logger
from jobs_hk.proxy_manager import ProxyPool
from jobs_hk.queue_manager import QueueMT
from jobs_hk.queue_manager import TaskFill
from jobs_hk.waiting import Waiting
from jobs_hk.web import JobGovHK


def worker(
        logger: Logger,
        queue: QueueMT,
        proxy_pool: ProxyPool
):
    current_thread_name = threading.current_thread().name

    waiting = Waiting()
    web = JobGovHK()
    web.set_proxy(**proxy_pool.get_proxy(current_thread_name))
    
    while (task_key := queue.get_pendding_task_key()):
        job = queue.get_task(task_key).job
        logger.info(f"Processing job: {job.name}")
        
        try:
            resp = web.job_card(job.order)
        except WebRetryExansted:
            queue.set_task_status("Pendding", task_key)
            proxy_pool.clear_proxy(current_thread_name)

            while True:
                try:
                    web.set_proxy(**proxy_pool.get_proxy(current_thread_name))
                except NeedWaiting:
                    waiting.random(show_info=False)
                    continue
                else:
                    break
            
            waiting.random(show_info=False)
            continue
        
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
    logger = get_logger("fill_multi_threads", multi_thread=True)
    lock = threading.Lock()
    
    queue = QueueMT(
        [
            TaskFill(job)
            for job in context.db.get_jobs_without_detailed()
        ],
        lock
    )
    
    proxy_pool = ProxyPool(
        host=context.project_config["proxy"]["host"],
        port_start=context.project_config["proxy"]["port_start"],
        offset=context.project_config["proxy"]["offset"],
        lock=lock
    )
    
    num_thread = int(context.project_config["proxy"]["offset"] * context.project_config["proxy"]["rate"])
    threads = [
        threading.Thread(
            target=worker,
            kwargs={
                "logger": logger,
                "queue": queue,
                "proxy_pool": proxy_pool,
            },
            name=f"Worker-{i + 1}"
        )
        for i in range(num_thread)
    ]
    
    for t in threads:
        t.start()
        time.sleep(3)
    for t in threads:
        t.join()
        