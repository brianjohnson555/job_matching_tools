import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import time
from proxies import proxies

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

def scrape_job_urls(pages=3, job_title="Data Scientist", location="Chicago", post_time=1):
    """Scrapes job post URLs from linkedin. Param "post_time" = time in days."""
    # Create empty job information with query data 
    job_urls = []

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
            time.sleep(random.uniform(2,4))
            # Get new page url and make request
            url = f"{API_url}keywords={job_title}&location={location}&f_TPR=r{int(post_time*86400)}&start={int(page*10)}"
            response = requests.get(url, headers=headers, proxies=proxies, cookies=cookies, timeout=10)

            if response.status_code != 200:
                print(f"Failed to retrieve jobs on page {page}: {response.status_code}")
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                link_elems = soup.find_all("a", class_="base-card__full-link")
                job_links = [link_elem.get("href") for link_elem in link_elems]
                job_urls += job_links
                print(f"{len(job_urls)} scraped successfully.")
        except Exception as e:
            print("Exception occured during scraping.")
            print(e)
            return job_urls
    print("Finished!")
    return job_urls