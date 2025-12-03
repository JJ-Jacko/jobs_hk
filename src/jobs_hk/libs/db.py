from sqlalchemy.exc import OperationalError

from jobs_hk.libs.waiting import Waiting


def db_retry(func: callable):
    """修饰访问数据库的函数断联后尝试重连

    Args:
        func (callable): 访问数据库的函数
    Raises:
        Exception: 多次尝试重连都无法连上
    """
    
    def wrapper(*args, **kwargs):
        count_retry = 0
        while True:
            if count_retry > 10:
                raise Exception("数据库连接异常")
            try:
                result = func(*args, **kwargs)
            except OperationalError:
                count_retry += 1
                Waiting.normal(10, "[n]s 后尝试重连")
                continue
            break
        return result
    
    return wrapper

