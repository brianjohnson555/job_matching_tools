import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import time
from datetime import datetime
from src.proxies import proxies

def get_fresh_cookies(base_url: str, user_agent: str):
    """Retrieves site cookies using the given url and user agent."""

    session = requests.Session() # Create session
    headers = {"User-Agent": user_agent}
    
    # Make request to url
    response = session.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch job search page ({response.status_code})")
        return None
    
    # Extract cookies
    cookies = session.cookies.get_dict()
    # cookies["li_gp"] = "MTsxNzQzMTAzMjU1OzA=" # add additional cookie (may not be required)
    return cookies

def parse_job_data(response):
    """Parses the job data from the given response text."""
    jobs = []
    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.find_all("div", class_="base-card")

    if not job_cards: #if no jobs found
        print("No more jobs found.")
        return None
    
    # Get job posting data from each posting:
    for job in job_cards:
        title_elem = job.find("h3", class_="base-search-card__title")
        company_elem = job.find("h4", class_="base-search-card__subtitle")
        location_elem = job.find("span", class_="job-search-card__location")
        time_elem = job.find("time")
        link_elem = job.find("a", class_="base-card__full-link")  # Job details link

        title = title_elem.text.strip() if title_elem else "N/A"
        company = company_elem.text.strip() if company_elem else "N/A"
        job_location = location_elem.text.strip() if location_elem else "N/A"
        job_link = link_elem.get("href") if link_elem else "N/A"
        job_time = time_elem.text.strip() if time_elem else "N/A"

        job_des = scrape_job_description_single(job_link) if link_elem else "N/A"

        jobs.append({"title": title, 
                     "company": company, 
                     "link": job_link, 
                     "posted time": job_time, 
                     "description": job_des,
                     "location": job_location,
                     })
    return jobs

def scrape_jobs(pages=3, job_title="Data Scientist", location="Chicago", post_time=1):
    """Scrapes job posting data from linkedin. Param "post_time" = time in days."""
    # Create empty job information with query data 
    job_data = {
                "query title": job_title,
                "query location": location,
                "query time": post_time,
                "query execution": datetime.today().strftime("%Y-%m-%d"),
                "jobs": [],
                }

    # Create URL, get cookies and header data:
    base_url = f"https://www.linkedin.com/jobs/search?keywords={job_title}&location={location}&f_TPR=r{int(post_time*86400)}&position=1&pageNum=0"
    API_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
    user_agent = UserAgent().random
    cookies = get_fresh_cookies(base_url, user_agent)
    headers = {
    "User-Agent": user_agent,
    "Csrf-Token": cookies["JSESSIONID"],
    "Referer": base_url,
    }

    if not cookies:
        print("Could not retrieve cookies. Exiting.")
        return None
    
    # Iterate through retrieval pages:
    for page in range(pages): 
        print(f"Scraping page {page}")
        try:
            # Get new page url and make request
            url = f"{API_url}keywords={job_title}&location={location}&f_TPR=r{int(post_time*86400)}&start={int(page*10)}"
            response = requests.get(url, headers=headers, proxies=proxies, cookies=cookies, timeout=10)

            if response.status_code != 200:
                print(f"Failed to retrieve jobs on page {page}: {response.status_code}")
            else:
                time.sleep(random.uniform(1,2))
                job_data["jobs"] += parse_job_data(response) # add to list
                print(f"{len(job_data["jobs"])} scraped successfully.")
        except Exception as e:
            print("Exception occured during scraping.")
            print(e)
            return job_data
    # Run job_des scrape again in case of any errors:
    print("Making sure all descriptions scraped...")
    job_data["jobs"] = scrape_job_descriptions(job_data["jobs"])
    print("Finished!")
    return job_data

def scrape_job_description_single(url: str):
    """Scrapes single job description from the given url. Returns str of job description."""
    headers = {"User-Agent": UserAgent().random, # make new random user for each job
                "Referer": "https://linkedin.com",
                }

    try:
        # Make request to full job posting page
        response = requests.get(url, headers=headers, proxies=proxies)

        if response.status_code != 200:
            print(f"Failed to retrieve job details: {response.status_code}")
            return None
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            job_description_elem = soup.find("div", class_="description__text")
            job_des = extract_clean_text(job_description_elem)
            return job_des
    except Exception as e: 
        print("Exception during description scrape.")
        print(e)
        return None

def scrape_job_descriptions(jobs: list):
    """Scrapes all job descriptions from the given jobs list. Returns jobs list."""
    idx = 0
    for job in jobs:
        if "description" not in job:
            print(f"Getting job desc number {idx}")
            headers = {"User-Agent": UserAgent().random, # make new random user for each job
                        "Referer": "https://linkedin.com",
                        }

            job_url = job["Link"]
            try:
                # Make request to full job posting page
                response = requests.get(job_url, headers=headers, proxies=proxies)

                if response.status_code != 200:
                    print(f"Failed to retrieve job details: {response.status_code}")
                else:
                    soup = BeautifulSoup(response.text, "html.parser")
                    job_description_elem = soup.find("div", class_="description__text")
                    job["description"] = extract_clean_text(job_description_elem)
            except Exception as e: 
                print("Exception during description scrape.")
                print(e)
                return jobs
        idx += 1

    return jobs

def extract_clean_text(tag) -> str:
    """Extracts clean text with spacing preserved from bs4.element.tag"""
    block_tags = {'p', 'li', 'br'}

    texts = []

    for child in tag.descendants:
        if child.name == 'br':
            texts.append('\n')
        elif child.name in block_tags:
            texts.append('\n' + child.get_text() + '\n')

    # Join, normalize newlines/spaces
    combined = ''.join(texts)
    lines = [line.strip() for line in combined.splitlines()]
    result = '\n'.join(line for line in lines if line)

    return result