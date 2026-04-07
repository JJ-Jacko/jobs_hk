import requests

from jobs_hk.libs.waiting import Waiting


def _web_retry(func: callable):
    """修饰 Web 请求的函数断联后尝试重连

    Args:
        func (callable):  Web 请求的函数
        
    Raises:
        Exception: 多次尝试重连都无法连上
    """
    
    def wrapper(*args, **kwargs):
        count_retry = 0
        while True:
            if count_retry > 10:
                raise Exception("网络连接异常")
            try:
                result = func(*args, **kwargs)
            except requests.exceptions.ConnectionError:
                count_retry += 1
                Waiting.normal(10, "[n]s 后尝试重连")
                continue
            break
        return result
    
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
    