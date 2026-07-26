import time
import threading
from logging import Logger

import jobs_hk.context as context
from jobs_hk.db import DBMT
from jobs_hk.exceptions import NeedWaiting
from jobs_hk.exceptions import WebRetryExansted
from jobs_hk.filters.job_search_filter import JobSearchFilter
from jobs_hk.log import get_logger
from jobs_hk.proxy_manager import ProxyPool
from jobs_hk.queue_manager import QueueMT
from jobs_hk.queue_manager import TaskSearch
from jobs_hk.waiting import Waiting
from jobs_hk.web import JobGovHK


def worker(
        logger: Logger,
        db: DBMT,
        queue: QueueMT,
        proxy_pool: ProxyPool
):
    current_thread_name = threading.current_thread().name
    
    waiting = Waiting()
    web = JobGovHK()
    web.set_proxy(**proxy_pool.get_proxy(current_thread_name))
    
    while (task_key := queue.get_pendding_task_key()):
        page = queue.get_task(task_key).page
        logger.info(f"Processing page: {page}")
        
        try:
            resp = web.job_search(page)
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
        
        filter = JobSearchFilter(resp.text)
        jobs = filter.get_jobs()
        
        for job in jobs:
            db.save_job(
                order=job["order"],
                name=job["name"],
                salary_type=job["salary_type"],
                salary_min=job["salary_min"],
                salary_max=job["salary_max"],
                address=job["address"]
            )
        
        queue.set_task_status("Completed", task_key)
        queue.set_task_date_time(task_key)
        waiting.random(show_info=False)


def fetch_total_pages():
    web = JobGovHK()
    resp = web.job_search()
    filter = JobSearchFilter(resp.text)

    return filter.get_total_pages()


def run():
    logger = get_logger("search_multi_threads", multi_thread=True)
    lock = threading.Lock()
    db = DBMT(context.DATA_BASE_FILE, lock, read_only=False)

    total_pages = fetch_total_pages()

    queue = QueueMT(
        [
            TaskSearch(i + 1)
            for i in range(total_pages)
        ],
        lock
    )
    
    proxy_pool = ProxyPool(
        host=context.CONFIG["proxy"]["host"],
        port_start=context.CONFIG["proxy"]["port_start"],
        offset=context.CONFIG["proxy"]["offset"],
        lock=lock
    )
    
    num_thread = int(context.CONFIG["proxy"]["offset"] * context.CONFIG["proxy"]["rate"])
    threads = [
        threading.Thread(
            target=worker,
            kwargs={
                "logger": logger,
                "db": db,
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