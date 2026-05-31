from urllib import parse
from typing import List

from bs4 import BeautifulSoup

from jobs_hk.other import match_re


class JobSearchFilter:
    soup: BeautifulSoup
    
    def __init__(self, html_content: str | bytes):
        self.soup = BeautifulSoup(html_content, "html.parser")
        
    def get_total_pages(self):
        """获取总页数"""
        
        a = self.soup.find("a", title="跳至最後一頁")
        if not a:
            raise Exception
        href = a.get("href")
        
        return int(match_re(r'page=(\d+)', href))

    def count_job_cards(self):
        """获取的工作卡的数量"""
        
        total_record = self.soup.find("strong", id="totalRecord")
        if not total_record:
            raise Exception
        
        return int(total_record.get_text(strip=True))

    def get_jobs(self):
        jobs: List[dict] = []
        
        job_list_table = self.soup.find("div", id="job_list_table")
        for job_table in job_list_table.find_all("div", class_="row item p-1 no-gutters"):
            no = job_table.get("data-prev")
            
            data_jobcard: str = job_table.get("data-jobcard")
            order = parse.unquote(match_re(r'order=([^&]+)', data_jobcard))
            
            for div in job_table.find_all("div"):
                if div.get("class"):
                    continue
                name = div.get_text(strip=True)
                if name.endswith("**"):
                    name_cleaned = name[:-2]
                else:
                    name_cleaned = name
                break
            else:
                raise Exception
            
            address = job_table.find("div", class_="menu_icon icon_address pb-2").get_text(strip=True)

            salary_src_str = job_table.find("div", class_="menu_icon icon_salary pb-2").get_text(strip=True)
            salary_type = match_re(r'（([^&]+)）', salary_src_str)

            # 范围类型
            if salary_src_str.find("-") != -1:
                salary_min_str = match_re(r'\$([\d,]+)', salary_src_str.split("-")[0])
                salary_max_str = match_re(r'\$([\d,]+)', salary_src_str.split("-")[1])
                
                jobs.append({
                    "no": no,
                    "order": order,
                    "name": name_cleaned,
                    "salary_type": salary_type,
                    "salary_min": int(salary_min_str.replace(',', '')),
                    "salary_max": int(salary_max_str.replace(',', '')),
                    "address": address
                })
            # 定值类型
            else:
                salary_str = match_re(r'\$([\d,]+)', salary_src_str)
            
                jobs.append({
                    "no": no,
                    "order": order,
                    "name": name_cleaned,
                    "salary_type": salary_type,
                    "salary_min": int(salary_str.replace(',', '')),
                    "salary_max": int(salary_str.replace(',', '')),
                    "address": address
                })
        
        return jobs
