import functools
import itertools
import socket
import time

import requests

from jobs_hk.exceptions import ProxyServerDisconnection
from jobs_hk.exceptions import WebRetryExansted


__all__ = [
    "proxy_server_active",
    "JobGovHK"
]


def web_retry(func):
    """
    Decorator for retrying web operations in case of disconnection.
    修饰 Web 请求的函数断联后尝试重连

    Raises:
        WebRetryExansted:
            Raised when multiple retry attempts fail.
            多次尝试重连都无法连上
    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in itertools.count(0):
            if attempt > 3:
                raise WebRetryExansted("Web connection failed after multiple retries")
            
            try:
                resp: requests.Response = func(*args, **kwargs)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout
            ):
                time.sleep(3)
                continue
            
            break
        
        return resp
    
    return wrapper


def proxy_server_active(
        host: str,
        port: int,
        timeout: float = 3.0
):
    """Check the proxy server active."""

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False
    
    return False


class JobGovHK:
    s: requests.Session
    
    def __init__(self):
        self.s = requests.session()
        self.s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
    
    def set_proxy(
            self,
            host: str,
            port: int
    ):
        """
        Raises:
            ProxyServerDisconnection:
                Raise it if the proxy server is disconnect.
        """
        
        if not proxy_server_active(host, port):
            raise ProxyServerDisconnection(host, port)
        
        proxy_url = f"http://{host}:{port}"        
        self.s.proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
    
    @web_retry
    def job_search(self, page: int = 1):
        url = "https://www1.jobs.gov.hk/0/tc/jobseeker/jobsearch/quickview/fulltime_na"
        params = {
            "direct": False,
            "page": page
        }
        resp = self.s.get(url, params=params)

        return resp

    @web_retry
    def job_card(self, order: str):
        url = "https://www1.jobs.gov.hk/0/tc/jobseeker/jobcard/"
        params = {
            "order": order,
            "from": "quickview",
            "for": "fulltime_na"
        }
        resp = self.s.post(url, params=params)

        return resp
    