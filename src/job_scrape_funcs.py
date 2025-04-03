import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import time
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

        jobs.append({"Title": title, 
                     "Company": company, 
                     "Link": job_link, 
                     "Posted time": job_time, 
                     "Description": job_des,
                     "Location": job_location,
                     })
    return jobs

def scrape_jobs(pages=3, job_title="Data Scientist", location="Chicago", post_time=1):
    """Scrapes job posting data from linkedin. Param "post_time" = time in days."""

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
    jobs = []
    for page in range(pages): 
        try:
            # Get new page url and make request
            url = f"{API_url}keywords={job_title}&location={location}&f_TPR=r{int(post_time*86400)}&start={int(page*10)}"
            response = requests.get(url, headers=headers, proxies=proxies, cookies=cookies, timeout=10)

            if response.status_code != 200:
                print(f"Failed to retrieve jobs on page {page}: {response.status_code}")
            else:
                time.sleep(random.uniform(1,2))
                jobs += parse_job_data(response) # add to list
                print(f"{len(jobs)} scraped successfully.")
        except:
            print("Exception occured during scraping.")
            return jobs
    # run job_des scrape again in case of any errors:
    print("Making sure all descriptions scraped...")
    jobs = scrape_job_descriptions(jobs)
    print("Finished!")
    return jobs

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
            job_des = job_description_elem.text.strip().replace("\n"," ") if job_description_elem else "N/A"
            return job_des
    except Exception as e: 
        print("Exception during description scrape.")
        print(e)
        return None

def scrape_job_descriptions(jobs: list):
    """Scrapes all job descriptions from the given jobs list. Returns jobs list."""
    idx = 0
    for job in jobs:
        if "Description" not in job:
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
                    job_des = job_description_elem.text.strip().replace("\n"," ") if job_description_elem else "N/A"
                    job["Description"] = job_des
            except Exception as e: 
                print("Exception during description scrape.")
                print(e)
                return jobs
        idx += 1

    return jobs

def check_num_desc(jobs):
    """Mini func to check how many job descriptions have been retrieved."""
    idx = 0
    for job in jobs:
        if "Description" in job:
            idx += 1
    return idx