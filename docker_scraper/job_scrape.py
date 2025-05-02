import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from proxies import proxies
import re
import json

filters = {"company":{"jobs via dice", "jobot", "hiretalent", "lensa"},
           "title": {"manager", "lead"},
           }

def scrape_job_single(url: str, query: str):
    """Scrapes job title, company, location, description from the given url. Returns dict of job data."""
    headers = {"User-Agent": UserAgent().random, # make new random user
                "Referer": "https://linkedin.com",
                }

    try:
        # Make request to full job posting page
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)

        if response.status_code != 200:
            print(f"Failed to retrieve job details: {response.status_code}")
            return None
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            job = soup.find("div", class_="details")
            title = job.find("h1", class_="top-card-layout__title").text.strip()
            company = job.find("a", class_="topcard__org-name-link").text.strip()

            if company.lower() in filters["company"] or any(title.lower().find(filt)>=0 for filt in filters["title"]):
                print("Job filtered out")
                return None
            
            location = job.find("span", class_="topcard__flavor--bullet").text.strip()
            job_des_elem = job.find("div", class_="description__text")
            job_des = extract_clean_text(job_des_elem)

            scripts = soup.find_all("script")
            post_time = "N/A"
            for script in scripts:
                if script.string and 'JobPosting' in script.string:
                    try:
                        json_text = re.search(r'({.*"@type":"JobPosting".*})', script.string, re.DOTALL)
                        job_json = json.loads(json_text.group(1))
                        post_time = job_json.get("datePosted")
                    except Exception as e:
                        print("Error parsing datePosted:", e)
            print("Job successfully scraped")
            return {"query": query,
                    "date": post_time, 
                    "title": title, 
                    "company": company, 
                    "link": url, 
                    "description": job_des,
                    "location": location,
                    }
    except Exception as e: 
        print("Exception during job scrape.")
        print(e)
        return None

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