from urllib import parse
from typing import List
from datetime import datetime

from bs4 import BeautifulSoup

from jobs_hk.libs.other import match_re


def fill_none(content: str):
    if content in ["-"]:
        return None
    else:
        content


class JobSearchFilter:
    soup: BeautifulSoup
    
    def __init__(self, html_content: str | bytes):
        self.soup = BeautifulSoup(html_content, "html.parser")

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
    
    
class JobCardFilter:
    soup: BeautifulSoup
    
    def __init__(self, html_content: str | bytes):
        self.soup = BeautifulSoup(html_content, "html.parser")

    def get_job_info(self):
        dt_formate = "%d/%m/%Y"
        
        num_str = self.soup.find("span", id="noVac").get_text(strip=True)
        try:
            num = int(num_str)
        except ValueError:
            if num_str in ["大量"]:
                num = 8888
            else:
                raise Exception
        post_date = datetime.strptime(
            self.soup.find("span", id="postedDt").get_text(strip=True),
            dt_formate
        ).date()
        company_name = self.soup.find("span", id="empName").get_text(strip=True)
        location = self.soup.find("span", id="locDesc").get_text(strip=True)
        industry = self.soup.find("span", id="indsDesc").get_text(strip=True)
        job_remark = self.soup.find("span", id="jobRemark").get_text(strip=True)
        edu_remark = self.soup.find("span", id="eduRemark").get_text(strip=True)
        compensation = self.soup.find("span", id="empTerm").get_text(strip=True)

        openup_remark = self.soup.find("span", id="openupRemark").get_text(strip=True)
        email = match_re(r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', openup_remark)
        phone = match_re(r'(\d{8})', openup_remark)
        phone_formated = f"{phone[:4]} {phone[4:]}" if phone else None
        alias = match_re(r'(\S(?:先生|小姐|女士))', openup_remark)
        
        prop_remark = fill_none(self.soup.find("span", id="propRemark").get_text(strip=True))
        
        return {
            "num": num,
            "post_date": post_date,
            "company_name": company_name,
            "location": location,
            "industry": industry,
            "job_remark": job_remark,
            "edu_remark": edu_remark,
            "compensation": compensation,
            "email": email,
            "phone": phone_formated,
            "alias": alias,
            "prop_remark": prop_remark
        }
