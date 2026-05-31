import functools
import itertools
import time

import requests


def _web_retry(func):
    """Decorator for retrying web operations in case of disconnection 修饰 Web 请求的函数断联后尝试重连

    Raises:
        Exception: Raised when multiple retry attempts fail 多次尝试重连都无法连上
    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in itertools.count(0):
            if attempt > 10:
                raise Exception("Web connection failed after multiple retries")
            
            try:
                resp: requests.Response = func(*args, **kwargs)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout
            ):
                time.sleep(10)
                continue
            
            if resp.status_code in (504, ):
                time.sleep(10)
                continue
            
            break
        
        return resp
    
    return wrapper


class Web:
    s = requests.session()
    s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
    
    @classmethod
    @_web_retry
    def job_search(cls, page: int = 1):
        url = "https://www1.jobs.gov.hk/0/tc/jobseeker/jobsearch/quickview/fulltime_na"
        params = {
            "direct": False,
            "page": page
        }
        resp = cls.s.get(url, params=params)

        return resp

    @classmethod
    @_web_retry
    def job_card(cls, order: str):
        url = "https://www1.jobs.gov.hk/0/tc/jobseeker/jobcard/"
        params = {
            "order": order,
            "from": "quickview",
            "for": "fulltime_na"
        }
        resp = requests.post(url, params=params)

        return resp
    