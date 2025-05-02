import json
from bs4 import BeautifulSoup
import url_scrape as scrape
# import boto3
# lambda_client = boto3.client("lambda")


def lambda_handler(event, context):
    print(json.dumps(event))
    job_title = str(event.get("query",""))
    location = str(event.get("location", "United States"))
    pages = int(event.get("pages", 1))
    post_time = float(event.get("post_time", 0.5))
    print("Request received")
        
    print("Starting job URL scrape")
    urls = scrape.scrape_job_urls(pages=pages, job_title=job_title, location=location, post_time=post_time)
    return {
            "url_list": urls,
            "query": job_title
            }
    # for url in urls:
    #     lambda_client.invoke(
    #         FunctionName='job-scraper',
    #         InvocationType='Event',  # Async
    #         Payload=json.dumps({'url': url, 'query': job_title.lower()})
    #     )