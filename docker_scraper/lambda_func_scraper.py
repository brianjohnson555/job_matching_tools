import json
from bs4 import BeautifulSoup
import docker_scraper.job_scrape as scrape
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table('YourTableName')

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        url = str(body.get("url",""))
        print("Request received with body")
    except:
        url = str(event.get("url",""))
        print("Request received without body")
        
    job_data = scrape.scrape_job_single(url)
    table.put_item(job_data)