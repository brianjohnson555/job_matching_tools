import json
from bs4 import BeautifulSoup
import url_scrape as scrape
import boto3
lambda_client = boto3.client("lambda")


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        job_title = str(body.get("job title",""))
        location = str(body.get("location", "United States"))
        pages = int(body.get("pages", 1))
        post_time = float(body.get("post time", 0.5))
        print("Request received with body")
    except:
        job_title = str(event.get("job title",""))
        location = str(event.get("location", "United States"))
        pages = int(event.get("pages", 1))
        post_time = float(event.get("post time", 0.5))
        print("Request received without body")
        
    print("Starting job URL scrape")
    urls = scrape.scrape_job_urls(pages=pages, job_title=job_title, location=location, post_time=post_time)
    
    for url in urls:
        lambda_client.invoke(
            FunctionName='job-scraper',
            InvocationType='Event',  # Async
            Payload=json.dumps({'url': url, 'query': job_title.lower()})
        )