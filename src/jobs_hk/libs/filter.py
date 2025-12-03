import re
from urllib import parse
from typing import List

from bs4 import BeautifulSoup

from jobs_hk.libs.datas import Job


class JobSearchFilter:
    soup: BeautifulSoup
    
    def __init__(self, html_content: str | bytes):
        self.soup = BeautifulSoup(html_content, "html.parser")

    def get_jobs(self):
        jobs: List[Job] = []
        
        job_list_table = self.soup.find("div", id="job_list_table")
        for job_table in job_list_table.find_all("div", class_="row item p-1 no-gutters"):
            no = job_table.get("data-prev")
            
            data_jobcard: str = job_table.get("data-jobcard")
            m = re.search(r'order=([^&]+)', data_jobcard)
            if not m:
                raise Exception
            order = parse.unquote(m.group(1))
            
            for div in job_table.find_all("div"):
                if div.get("class"):
                    continue
                name = div.get_text(strip=True)
                break
            else:
                raise Exception
            
            salary = job_table.find("div", class_="menu_icon icon_salary pb-2").get_text(strip=True)

            address = job_table.find("div", class_="menu_icon icon_address pb-2").get_text(strip=True)
            
            jobs.append(Job(
                no=no,
                order=order,
                name=name,
                salary=salary,
                address=address
            ))
        
        return jobs
