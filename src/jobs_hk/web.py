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


class JobGovHK:
    s: requests.Session
    
    def __init__(
            self,
            proxy_host: str = None,
            proxy_port: int = None
    ):
        self.s = requests.session()
        
        self.s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
        
        if all((proxy_host, proxy_port)):
            proxy_url = f"http://{proxy_host}:{proxy_port}"        
            self.s.proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }
    
    @_web_retry
    def job_search(self, page: int = 1):
        url = "https://www1.jobs.gov.hk/0/tc/jobseeker/jobsearch/quickview/fulltime_na"
        params = {
            "direct": False,
            "page": page
        }
        resp = self.s.get(url, params=params)

        return resp

    @_web_retry
    def job_card(self, order: str):
        url = "https://www1.jobs.gov.hk/0/tc/jobseeker/jobcard/"
        params = {
            "order": order,
            "from": "quickview",
            "for": "fulltime_na"
        }
        resp = self.s.post(url, params=params)

        return resp
    