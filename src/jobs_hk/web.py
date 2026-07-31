import functools
import itertools
import socket
import time

import httpx

from jobs_hk import context
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
                resp: httpx.Response = func(*args, **kwargs)
            except (
                httpx.ConnectError,
                httpx.ConnectTimeout
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
    client: httpx.Client
    
    def __init__(self):
        self.client = None
        self.__reset_client()

    def __reset_client(
            self,
            porxy_url: str = None
    ):
        headers = {
            "User-Agent": context.USER_AGENT
        }
    
        if isinstance(self.client, httpx.Client):
            self.client.close()
        
        self.client = httpx.Client(
            base_url=context.BASE_URL,
            headers=headers,
            proxy=porxy_url
        )
    
    def set_proxy(
            self,
            host: str,
            port: int
    ):        
        self.__reset_client(f"http://{host}:{port}")
    
    @web_retry
    def job_search(self, page: int = 1):
        url = "0/tc/jobseeker/jobsearch/quickview/fulltime_na/"
        params = {
            "direct": False,
            "page": page
        }
        resp = self.client.get(url, params=params)

        return resp

    @web_retry
    def job_card(self, order: str):
        url = "0/tc/jobseeker/jobcard/"
        params = {
            "order": order,
            "from": "quickview",
            "for": "fulltime_na"
        }
        resp = self.client.post(url, params=params)

        return resp
    