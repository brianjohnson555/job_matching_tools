import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import time

def get_fresh_cookies(base_url, user_agent):

    session = requests.Session()
    headers = {"User-Agent": user_agent}
    
    # Load Job Search Page to get Updated Cookies
    response = session.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch job search page ({response.status_code})")
        return None
    
    # Extract Updated Cookies
    cookies = session.cookies.get_dict()
    cookies["li_gp"] = "MTsxNzQzMTAzMjU1OzA="
    return cookies

def scrape_linkedin_jobs(proxies, pages=3, job_title="Data Scientist"):
    base_url = f"https://www.linkedin.com/jobs/search?keywords={job_title}&location=Chicago&position=1&pageNum=0"
    API_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
    user_agent = UserAgent().random
    jobs = []

    cookies = get_fresh_cookies(base_url, user_agent)

    if not cookies:
        print("Could not retrieve cookies. Exiting.")
        return jobs

    headers = {
    "User-Agent": user_agent,
    "Csrf-Token": cookies["JSESSIONID"],
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "DNT": "1",
    "Host": "www.linkedin.com",
    "Priority": "u=4",
    "Referer": base_url,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    }

    for page in range(pages):
        url = f"{API_url}keywords={job_title}&location=Chicago&start={int(page*10)}"
        response = requests.get(url, headers=headers, proxies=proxies, cookies=cookies, timeout=10)

        if response.status_code != 200:
            print(f"Failed to retrieve jobs: {response.status_code}")
            return jobs

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("div", class_="base-card")

        for job in job_cards:
            title_elem = job.find("h3", class_="base-search-card__title")
            company_elem = job.find("h4", class_="base-search-card__subtitle")
            location_elem = job.find("span", class_="job-search-card__location")
            time_elem = job.find("time")
            link_elem = job.find("a", class_="base-card__full-link")  # Job details link

            title = title_elem.text.strip() if title_elem else "N/A"
            company = company_elem.text.strip() if company_elem else "N/A"
            location = location_elem.text.strip() if location_elem else "N/A"
            job_link = link_elem.get("href") if link_elem else "N/A"
            job_time = time_elem.text.strip() if time_elem else "N/A"

            jobs.append({"Title": title, "Company": company, "Link": job_link, "Posted time": job_time})
        print(f"{len(jobs)} scraped successfully.")
        time.sleep(random.uniform(1, 5))
    print("Scraping job descriptions...")
    jobs = scrape_job_descriptions(jobs, proxies)
    print("Finished!")
    return jobs

def scrape_job_descriptions(jobs, proxies):
    for job in jobs:
        if "Description" not in job:
            headers = {"User-Agent": UserAgent().random,
                        "Referer": "https://linkedin.com",
                        }

            job_url = job["Link"]
            response = requests.get(job_url, headers=headers, proxies=proxies)

            if response.status_code != 200:
                print(f"Failed to retrieve job details: {response.status_code}")
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                job_description_elem = soup.find("div", class_="description__text")
                job_des = job_description_elem.text.strip().replace("\n","") if job_description_elem else "N/A"
                job["Description"] = job_des

    return jobs