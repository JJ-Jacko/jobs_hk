from datetime import datetime

from bs4 import BeautifulSoup

from jobs_hk.libs.other import match_re
from jobs_hk.libs.other import fill_none


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
