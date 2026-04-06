import requests

from jobs_hk.libs.waiting import Waiting


def web_retry(func: callable):
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


@web_retry
def url_get_job_search(page: int = 1):
    url = "https://www1.jobs.gov.hk/0/tc/jobseeker/jobsearch/quickview/fulltime_na"
    params = {
        "direct": False,
        "page": page
    }
    resp = requests.get(url, params)

    return resp


@web_retry
def url_get_job_card(order: str):
    url = "https://www1.jobs.gov.hk/0/tc/jobseeker/jobcard/"
    params = {
        "order": order,
        "from": "quickview",
        "for": "fulltime_na"
    }
    resp = requests.post(url, params=params)

    return resp